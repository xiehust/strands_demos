"""Agent lifecycle management using Claude Agent SDK."""
from typing import AsyncIterator, Optional, Any
from uuid import uuid4
from datetime import datetime
import logging
import os
import json

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
    ResultMessage,
    HookMatcher,
)

from database import db
from config import settings, get_bedrock_model_id
from .session_manager import session_manager

logger = logging.getLogger(__name__)


def _configure_claude_environment():
    """Configure environment variables for Claude Code CLI."""
    # Set ANTHROPIC_API_KEY if configured
    if settings.anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key

    # Set ANTHROPIC_BASE_URL if configured (for custom endpoints)
    if settings.anthropic_base_url:
        os.environ["ANTHROPIC_BASE_URL"] = settings.anthropic_base_url
    elif "ANTHROPIC_BASE_URL" in os.environ:
        # Clear it if not configured but exists in environment
        del os.environ["ANTHROPIC_BASE_URL"]

    # Set CLAUDE_CODE_USE_BEDROCK if enabled
    if settings.claude_code_use_bedrock:
        os.environ["CLAUDE_CODE_USE_BEDROCK"] = "true"
    elif "CLAUDE_CODE_USE_BEDROCK" in os.environ:
        del os.environ["CLAUDE_CODE_USE_BEDROCK"]

    # Set CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS if enabled
    if settings.claude_code_disable_experimental_betas:
        os.environ["CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS"] = "true"
    elif "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS" in os.environ:
        del os.environ["CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS"]

    logger.info(f"Claude environment configured - Bedrock: {settings.claude_code_use_bedrock}, Base URL: {settings.anthropic_base_url or 'default'}")


async def pre_tool_logger(
    input_data: dict,
    tool_use_id: str | None,
    context: Any
) -> dict:
    """Log tool usage before execution."""
    tool_name = input_data.get('tool_name', 'unknown')
    tool_input = input_data.get('tool_input', {})
    logger.info(f"[PRE-TOOL] Tool: {tool_name}, Input keys: {list(tool_input.keys())}")
    return {}


async def dangerous_command_blocker(
    input_data: dict,
    tool_use_id: str | None,
    context: Any
) -> dict:
    """Block dangerous bash commands."""
    if input_data.get('tool_name') == 'Bash':
        command = input_data.get('tool_input', {}).get('command', '')

        dangerous_patterns = [
            'rm -rf /',
            'rm -rf ~',
            'dd if=/dev/zero',
            ':(){:|:&};:',
            '> /dev/sda',
        ]

        for pattern in dangerous_patterns:
            if pattern in command:
                logger.warning(f"[BLOCKED] Dangerous command: {command}")
                return {
                    'hookSpecificOutput': {
                        'hookEventName': 'PreToolUse',
                        'permissionDecision': 'deny',
                        'permissionDecisionReason': f'Dangerous command blocked: {pattern}'
                    }
                }
    return {}


class AgentManager:
    """Manages agent lifecycle using Claude Agent SDK.

    Uses ClaudeSDKClient for stateful, multi-turn conversations with Claude.
    Claude Code (underlying SDK) has built-in support for Skills and MCP servers.
    """

    def __init__(self):
        self._clients: dict[str, ClaudeSDKClient] = {}

    async def _build_options(
        self,
        agent_config: dict,
        enable_skills: bool,
        enable_mcp: bool,
        resume_session_id: Optional[str] = None
    ) -> ClaudeAgentOptions:
        """Build ClaudeAgentOptions from agent configuration.

        Args:
            agent_config: Agent configuration dictionary
            enable_skills: Whether to enable skills
            enable_mcp: Whether to enable MCP servers
            resume_session_id: Optional session ID to resume (for multi-turn conversations)
        """

        # Build allowed tools list - use directly from config if provided
        allowed_tools = list(agent_config.get("allowed_tools", []))

        # If no allowed_tools specified, fall back to enable flags for backwards compatibility
        if not allowed_tools:
            if agent_config.get("enable_bash_tool", True):
                allowed_tools.append("Bash")

            if agent_config.get("enable_file_tools", True):
                for tool_name in ["Read", "Write", "Edit", "Glob", "Grep"]:
                    allowed_tools.append(tool_name)

            if agent_config.get("enable_web_tools", True):
                for tool_name in ["WebFetch", "WebSearch"]:
                    allowed_tools.append(tool_name)

        # Always allow Skill tool (not exposed to user)
        if "Skill" not in allowed_tools:
            allowed_tools.append("Skill")

        # MCP servers configuration
        mcp_servers = {}

        # Add external MCP servers if enabled
        if enable_mcp and agent_config.get("mcp_ids"):
            for mcp_id in agent_config["mcp_ids"]:
                mcp_config = await db.mcp_servers.get(mcp_id)
                if mcp_config:
                    connection_type = mcp_config.get("connection_type", "stdio")
                    config = mcp_config.get("config", {})

                    if connection_type == "stdio":
                        mcp_servers[mcp_id] = {
                            "type": "stdio",
                            "command": config.get("command"),
                            "args": config.get("args", []),
                        }
                    elif connection_type == "sse":
                        mcp_servers[mcp_id] = {
                            "type": "sse",
                            "url": config.get("url"),
                        }
                    elif connection_type == "http":
                        mcp_servers[mcp_id] = {
                            "type": "http",
                            "url": config.get("url"),
                        }

        # Build system prompt
        system_prompt = agent_config.get("system_prompt")
        if system_prompt:
            system_prompt_config = system_prompt
        else:
            system_prompt_config = f"You are {agent_config.get('name', 'an AI assistant')}. {agent_config.get('description', '')}"

        # Build hooks
        hooks = {}

        if agent_config.get("enable_tool_logging", True):
            hooks["PreToolUse"] = [
                HookMatcher(hooks=[pre_tool_logger])
            ]

        if agent_config.get("enable_safety_checks", True):
            if "PreToolUse" not in hooks:
                hooks["PreToolUse"] = []
            hooks["PreToolUse"].append(
                HookMatcher(matcher="Bash", hooks=[dangerous_command_blocker])
            )

        # Determine permission mode
        permission_mode = agent_config.get("permission_mode", "default")

        # Get model from config and convert to Bedrock model ID if using Bedrock
        model = agent_config.get("model")
        if model and settings.claude_code_use_bedrock:
            model = get_bedrock_model_id(model)
            logger.info(f"Using Bedrock model: {model}")

        return ClaudeAgentOptions(
            system_prompt=system_prompt_config,
            allowed_tools=allowed_tools if allowed_tools else None,
            mcp_servers=mcp_servers if mcp_servers else None,
            permission_mode=permission_mode,
            model=model,
            cwd=agent_config.get("working_directory") or settings.agent_workspace_dir,
            setting_sources=['project'],
            hooks=hooks if hooks else None,
            resume=resume_session_id,  # Resume from previous session for multi-turn
        )

    async def _save_message(
        self,
        session_id: str,
        role: str,
        content: list[dict],
        model: Optional[str] = None
    ) -> dict:
        """Save a message to the database.

        Args:
            session_id: The session ID
            role: Message role ('user' or 'assistant')
            content: Message content blocks
            model: Optional model name for assistant messages

        Returns:
            The saved message dict
        """
        message_data = {
            "id": str(uuid4()),
            "session_id": session_id,
            "role": role,
            "content": content,
            "model": model,
            "created_at": datetime.now().isoformat(),
        }
        await db.messages.put(message_data)
        return message_data

    async def get_session_messages(self, session_id: str) -> list[dict]:
        """Get all messages for a session.

        Args:
            session_id: The session ID

        Returns:
            List of message dicts ordered by timestamp
        """
        return await db.messages.list_by_session(session_id)

    async def run_conversation(
        self,
        agent_id: str,
        user_message: str,
        session_id: Optional[str] = None,
        enable_skills: bool = False,
        enable_mcp: bool = False,
    ) -> AsyncIterator[dict]:
        """Run conversation with agent and stream responses.

        Uses ClaudeSDKClient for multi-turn conversations with Claude.
        Claude Code has built-in support for Skills via the Skill tool.

        For multi-turn conversations, pass the same session_id to resume
        the conversation from where it left off.
        """
        # Check if this is a new session or resuming an existing one
        is_new_session = session_id is None
        if not session_id:
            session_id = str(uuid4())

        # Get agent config
        agent_config = await db.agents.get(agent_id)
        if not agent_config:
            yield {
                "type": "error",
                "error": f"Agent {agent_id} not found",
            }
            return

        logger.info(f"Running conversation with agent {agent_id}, session {session_id}, is_new={is_new_session}")
        logger.info(f"Agent config: {agent_config}")

        # Send session_start event immediately so frontend can track session_id for stopping
        yield {
            "type": "session_start",
            "sessionId": session_id,
        }

        # Store/update session
        title = user_message[:50] + "..." if len(user_message) > 50 else user_message
        await session_manager.store_session(session_id, agent_id, title)

        # Save user message to database
        await self._save_message(
            session_id=session_id,
            role="user",
            content=[{"type": "text", "text": user_message}]
        )

        # Configure Claude environment variables
        _configure_claude_environment()

        # Build options - use resume parameter if continuing an existing session
        resume_id = session_id if not is_new_session else None
        options = await self._build_options(agent_config, enable_skills, enable_mcp, resume_id)
        logger.info(f"Built options - allowed_tools: {options.allowed_tools}, permission_mode: {options.permission_mode}, resume: {resume_id}")
        logger.info(f"MCP servers: {options.mcp_servers}")
        logger.info(f"Working directory: {options.cwd}")

        # Collect assistant response content for saving
        assistant_content = []
        assistant_model = None

        try:
            logger.info(f"Creating ClaudeSDKClient...")
            async with ClaudeSDKClient(options=options) as client:
                # Store client for potential interruption
                self._clients[session_id] = client
                logger.info(f"ClaudeSDKClient created and stored for session {session_id}")

                try:
                    logger.info(f"Sending query: {user_message[:100]}...")
                    # Send query
                    await client.query(user_message)
                    logger.info(f"Query sent, waiting for response...")

                    # Stream responses
                    message_count = 0
                    async for message in client.receive_response():
                        message_count += 1
                        logger.debug(f"Received message {message_count}: {type(message).__name__}")
                        formatted = self._format_message(message, agent_config, session_id)
                        if formatted:
                            logger.debug(f"Formatted message type: {formatted.get('type')}")

                            # Collect content for saving
                            if formatted.get('type') == 'assistant' and formatted.get('content'):
                                assistant_content.extend(formatted['content'])
                                assistant_model = formatted.get('model')

                            yield formatted

                            # If this is an AskUserQuestion, stop and wait for user input
                            if formatted.get('type') == 'ask_user_question':
                                logger.info(f"AskUserQuestion detected, stopping to wait for user input")
                                # Save assistant message before returning
                                if assistant_content:
                                    await self._save_message(
                                        session_id=session_id,
                                        role="assistant",
                                        content=assistant_content,
                                        model=assistant_model
                                    )
                                return

                        # If it's a result message, include session info
                        if isinstance(message, ResultMessage):
                            logger.info(f"Conversation complete. Total messages: {message_count}")

                            # Save assistant message
                            if assistant_content:
                                await self._save_message(
                                    session_id=session_id,
                                    role="assistant",
                                    content=assistant_content,
                                    model=assistant_model
                                )

                            yield {
                                "type": "result",
                                "session_id": session_id,
                                "duration_ms": getattr(message, 'duration_ms', 0),
                                "total_cost_usd": getattr(message, 'total_cost_usd', None),
                                "num_turns": getattr(message, 'num_turns', 1),
                            }
                finally:
                    # Remove client from tracking when done
                    self._clients.pop(session_id, None)
                    logger.info(f"Client removed from tracking for session {session_id}")

        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Error in conversation: {e}")
            logger.error(f"Full traceback:\n{error_traceback}")
            yield {
                "type": "error",
                "error": str(e),
                "detail": error_traceback,
            }

    def _format_message(self, message: Any, agent_config: dict, session_id: Optional[str] = None) -> Optional[dict]:
        """Format SDK message to API response format."""

        if isinstance(message, AssistantMessage):
            content_blocks = []

            for block in message.content:
                if isinstance(block, TextBlock):
                    content_blocks.append({
                        "type": "text",
                        "text": block.text
                    })
                elif isinstance(block, ToolUseBlock):
                    # Check if this is an AskUserQuestion tool call
                    if block.name == "AskUserQuestion":
                        # Return special ask_user_question event
                        questions = block.input.get("questions", [])
                        event = {
                            "type": "ask_user_question",
                            "toolUseId": block.id,
                            "questions": questions
                        }
                        # Include session_id so frontend can continue the conversation
                        if session_id:
                            event["sessionId"] = session_id
                        return event
                    else:
                        content_blocks.append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input
                        })
                elif isinstance(block, ToolResultBlock):
                    content_blocks.append({
                        "type": "tool_result",
                        "tool_use_id": block.tool_use_id,
                        "content": str(block.content) if block.content else None,
                        "is_error": getattr(block, 'is_error', False)
                    })

            if content_blocks:
                return {
                    "type": "assistant",
                    "content": content_blocks,
                    "model": getattr(message, 'model', agent_config.get("model", "claude-sonnet-4-20250514"))
                }

        elif isinstance(message, ResultMessage):
            # Return None here, we handle ResultMessage separately to include session_id
            return None

        return None

    async def continue_with_answer(
        self,
        agent_id: str,
        session_id: str,
        tool_use_id: str,
        answers: dict[str, str],
        enable_skills: bool = False,
        enable_mcp: bool = False,
    ) -> AsyncIterator[dict]:
        """Continue conversation by providing answers to AskUserQuestion.

        This method sends the user's answers as a user message to continue
        the conversation after Claude asked questions.

        Args:
            agent_id: The agent ID
            session_id: The session ID (required for conversation continuity)
            tool_use_id: The tool_use_id from the AskUserQuestion event (for reference)
            answers: Dictionary mapping question text to answer text
            enable_skills: Whether to enable skills
            enable_mcp: Whether to enable MCP servers

        Yields:
            Formatted messages from the agent
        """
        # Get agent config
        agent_config = await db.agents.get(agent_id)
        if not agent_config:
            yield {
                "type": "error",
                "error": f"Agent {agent_id} not found",
            }
            return

        logger.info(f"Continuing conversation with answer for agent {agent_id}, session {session_id}")
        logger.info(f"Tool use ID: {tool_use_id}, Answers: {answers}")

        # Configure Claude environment variables
        _configure_claude_environment()

        # Build options with resume to continue the session
        options = await self._build_options(agent_config, enable_skills, enable_mcp, resume_session_id=session_id)

        # Format answers as a user message
        answer_message = json.dumps({"answers": answers}, indent=2)

        # Save user answer to database
        await self._save_message(
            session_id=session_id,
            role="user",
            content=[{"type": "text", "text": f"User answers:\n{answer_message}"}]
        )

        # Collect assistant response content for saving
        assistant_content = []
        assistant_model = None

        try:
            logger.info(f"Creating ClaudeSDKClient for answer continuation with resume={session_id}...")
            async with ClaudeSDKClient(options=options) as client:
                # Store client for potential interruption
                self._clients[session_id] = client

                # Send the answers as a regular user message
                await client.query(answer_message)
                logger.info(f"Answer sent, waiting for response...")

                message_count = 0
                async for message in client.receive_response():
                    message_count += 1
                    logger.debug(f"Received message {message_count}: {type(message).__name__}")
                    formatted = self._format_message(message, agent_config, session_id)
                    if formatted:
                        logger.debug(f"Formatted message type: {formatted.get('type')}")

                        # Collect content for saving
                        if formatted.get('type') == 'assistant' and formatted.get('content'):
                            assistant_content.extend(formatted['content'])
                            assistant_model = formatted.get('model')

                        yield formatted

                        # If this is an AskUserQuestion, stop and wait for user input
                        if formatted.get('type') == 'ask_user_question':
                            logger.info(f"AskUserQuestion detected, stopping to wait for user input")
                            if assistant_content:
                                await self._save_message(
                                    session_id=session_id,
                                    role="assistant",
                                    content=assistant_content,
                                    model=assistant_model
                                )
                            return

                    if isinstance(message, ResultMessage):
                        logger.info(f"Conversation continued successfully. Total messages: {message_count}")

                        # Save assistant message
                        if assistant_content:
                            await self._save_message(
                                session_id=session_id,
                                role="assistant",
                                content=assistant_content,
                                model=assistant_model
                            )

                        yield {
                            "type": "result",
                            "session_id": session_id,
                            "duration_ms": getattr(message, 'duration_ms', 0),
                            "total_cost_usd": getattr(message, 'total_cost_usd', None),
                            "num_turns": getattr(message, 'num_turns', 1),
                        }

        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Error continuing conversation with answer: {e}")
            logger.error(f"Full traceback:\n{error_traceback}")
            yield {
                "type": "error",
                "error": str(e),
                "detail": error_traceback,
            }
        finally:
            self._clients.pop(session_id, None)

    async def disconnect_all(self):
        """Disconnect all active clients."""
        for session_id, client in list(self._clients.items()):
            try:
                logger.info(f"Disconnecting client for session {session_id}")
                # Try to interrupt if running
                await client.interrupt()
            except Exception as e:
                logger.error(f"Error disconnecting client {session_id}: {e}")
        self._clients.clear()

    async def interrupt_session(self, session_id: str) -> dict:
        """Interrupt a running session.

        Args:
            session_id: The session ID to interrupt

        Returns:
            Dict with status information
        """
        client = self._clients.get(session_id)
        if not client:
            logger.warning(f"No active client found for session {session_id}")
            return {
                "success": False,
                "message": f"No active session found with ID {session_id}",
            }

        try:
            logger.info(f"Interrupting session {session_id}")
            await client.interrupt()
            logger.info(f"Session {session_id} interrupted successfully")
            return {
                "success": True,
                "message": "Session interrupted successfully",
            }
        except Exception as e:
            logger.error(f"Error interrupting session {session_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to interrupt session: {str(e)}",
            }

    async def run_skill_creator_conversation(
        self,
        skill_name: str,
        skill_description: str,
        user_message: Optional[str] = None,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AsyncIterator[dict]:
        """Run a skill creation conversation with a specialized Skill Creator Agent.

        This creates a temporary agent configuration specifically for skill creation,
        using the skill-creator skill to guide the process.

        Args:
            skill_name: Name of the skill to create
            skill_description: Description of what the skill should do
            user_message: Optional follow-up message for iterating on the skill
            session_id: Optional session ID for continuing conversation
            model: Optional model to use (defaults to claude-sonnet-4-5-20250514)

        Yields:
            Formatted messages from the agent
        """
        # Check if resuming or new session
        is_new_session = session_id is None
        if not session_id:
            session_id = str(uuid4())

        # Build the initial prompt or use the follow-up message
        if user_message:
            # This is a follow-up message for iteration
            prompt = user_message
        else:
            # Initial skill creation request
            prompt = f"""Please create a new skill with the following specifications:

**Skill Name:** {skill_name}
**Skill Description:** {skill_description}

Use the skill-creator skill (invoke /skill-creator) to guide your skill creation process. Follow the workflow:
1. Understand the skill requirements from the description above
2. Plan reusable contents (scripts, references, assets) if needed
3. Initialize the skill using the init_skill.py script
4. Edit SKILL.md and create any necessary files
5. Test any scripts you create

Create the skill in the `.claude/skills/` directory within the current workspace."""

        # Build system prompt for skill creator agent
        system_prompt = f"""You are a Skill Creator Agent specialized in creating Claude Code skills.

Your task is to help users create high-quality skills that extend Claude's capabilities.

IMPORTANT GUIDELINES:
1. Always use the skill-creator skill (invoke /skill-creator) to get guidance on skill creation best practices
2. Follow the skill creation workflow from the skill-creator skill
3. Create skills in the `.claude/skills/` directory
4. Ensure SKILL.md has proper YAML frontmatter with name and description
5. Keep skills concise and focused - only include what Claude needs
6. Test any scripts you create before completing

The skill-creator skill provides comprehensive guidance on:
- Skill anatomy and structure
- Progressive disclosure design
- When to use scripts, references, and assets
- Best practices for SKILL.md content

Current task: Create a skill named "{skill_name}" that {skill_description}"""

        # Create temporary agent config for skill creation
        agent_config = {
            "name": f"skill-creator-{session_id[:8]}",
            "description": "Temporary agent for skill creation",
            "system_prompt": system_prompt,
            "allowed_tools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "Skill"],
            "permission_mode": "acceptEdits",
            "working_directory": settings.agent_workspace_dir,
            "enable_tool_logging": True,
            "enable_safety_checks": True,
            "model": model or "claude-sonnet-4-5-20250929",  # Default to Sonnet 4.5
        }

        logger.info(f"Running skill creator conversation for '{skill_name}', session {session_id}, model {agent_config['model']}")

        # Send session_start event immediately so frontend can track session_id for stopping
        yield {
            "type": "session_start",
            "sessionId": session_id,
        }

        # Store session
        title = f"Creating skill: {skill_name}"
        await session_manager.store_session(session_id, "skill-creator", title)

        # Configure Claude environment variables
        _configure_claude_environment()

        # Build options with resume if continuing
        resume_id = session_id if not is_new_session else None
        options = await self._build_options(agent_config, enable_skills=True, enable_mcp=False, resume_session_id=resume_id)
        logger.info(f"Skill creator options - allowed_tools: {options.allowed_tools}, resume: {resume_id}")
        logger.info(f"Working directory: {options.cwd}")

        try:
            logger.info(f"Creating ClaudeSDKClient for skill creation...")
            async with ClaudeSDKClient(options=options) as client:
                # Store client for potential interruption
                self._clients[session_id] = client
                logger.info(f"ClaudeSDKClient created and stored for session {session_id}")

                try:
                    logger.info(f"Sending skill creation query...")
                    await client.query(prompt)
                    logger.info(f"Query sent, waiting for response...")

                    message_count = 0
                    async for message in client.receive_response():
                        message_count += 1
                        logger.debug(f"Received message {message_count}: {type(message).__name__}")
                        formatted = self._format_message(message, agent_config, session_id)
                        if formatted:
                            logger.debug(f"Formatted message type: {formatted.get('type')}")
                            yield formatted

                            # If this is an AskUserQuestion, stop and wait for user input
                            if formatted.get('type') == 'ask_user_question':
                                logger.info(f"AskUserQuestion detected, stopping to wait for user input")
                                return

                        if isinstance(message, ResultMessage):
                            logger.info(f"Skill creation conversation complete. Total messages: {message_count}")
                            yield {
                                "type": "result",
                                "session_id": session_id,
                                "duration_ms": getattr(message, 'duration_ms', 0),
                                "total_cost_usd": getattr(message, 'total_cost_usd', None),
                                "num_turns": getattr(message, 'num_turns', 1),
                                "skill_name": skill_name,
                            }
                finally:
                    # Remove client from tracking when done
                    self._clients.pop(session_id, None)
                    logger.info(f"Client removed from tracking for session {session_id}")

        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Error in skill creation conversation: {e}")
            logger.error(f"Full traceback:\n{error_traceback}")
            yield {
                "type": "error",
                "error": str(e),
                "detail": error_traceback,
            }


# Global instance
agent_manager = AgentManager()
