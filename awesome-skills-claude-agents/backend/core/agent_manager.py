"""Agent lifecycle management using Claude Agent SDK."""
from typing import AsyncIterator, Optional, Any
from uuid import uuid4
import logging
import os

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
from config import settings
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

    logger.debug(f"Claude environment configured - Bedrock: {settings.claude_code_use_bedrock}, Base URL: {settings.anthropic_base_url or 'default'}")


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

    def _build_options(self, agent_config: dict, enable_skills: bool, enable_mcp: bool) -> ClaudeAgentOptions:
        """Build ClaudeAgentOptions from agent configuration."""

        # Build allowed tools list
        allowed_tools = list(agent_config.get("allowed_tools", []))

        # Add built-in tools based on config
        if agent_config.get("enable_bash_tool", True):
            if "Bash" not in allowed_tools:
                allowed_tools.append("Bash")

        if agent_config.get("enable_file_tools", True):
            for tool_name in ["Read", "Write", "Edit", "Glob", "Grep"]:
                if tool_name not in allowed_tools:
                    allowed_tools.append(tool_name)

        if agent_config.get("enable_web_tools", False):
            for tool_name in ["WebFetch", "WebSearch"]:
                if tool_name not in allowed_tools:
                    allowed_tools.append(tool_name)

        # Always allow Skill tool
        allowed_tools.append("Skill")

        # MCP servers configuration
        mcp_servers = {}

        # Add external MCP servers if enabled
        if enable_mcp and agent_config.get("mcp_ids"):
            for mcp_id in agent_config["mcp_ids"]:
                mcp_config = db.mcp_servers.get(mcp_id)
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

        return ClaudeAgentOptions(
            system_prompt=system_prompt_config,
            allowed_tools=allowed_tools if allowed_tools else None,
            mcp_servers=mcp_servers if mcp_servers else None,
            permission_mode=permission_mode,
            max_turns=agent_config.get("max_turns"),
            cwd=agent_config.get("working_directory") or settings.agent_workspace_dir,
            hooks=hooks if hooks else None,
        )

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
        """
        # Get or create session
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

        logger.info(f"Running conversation with agent {agent_id}, session {session_id}")

        # Store session
        title = user_message[:50] + "..." if len(user_message) > 50 else user_message
        await session_manager.store_session(session_id, agent_id, title)

        # Configure Claude environment variables
        _configure_claude_environment()

        # Build options
        options = self._build_options(agent_config, enable_skills, enable_mcp)

        try:
            async with ClaudeSDKClient(options=options) as client:
                # Send query
                await client.query(user_message)

                # Stream responses
                async for message in client.receive_response():
                    formatted = self._format_message(message, agent_config)
                    if formatted:
                        yield formatted

                    # If it's a result message, include session info
                    if isinstance(message, ResultMessage):
                        yield {
                            "type": "result",
                            "session_id": session_id,
                            "duration_ms": getattr(message, 'duration_ms', 0),
                            "total_cost_usd": getattr(message, 'total_cost_usd', None),
                            "num_turns": getattr(message, 'num_turns', 1),
                        }

        except Exception as e:
            logger.error(f"Error in conversation: {e}")
            yield {
                "type": "error",
                "error": str(e),
            }

    def _format_message(self, message: Any, agent_config: dict) -> Optional[dict]:
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

    async def disconnect_all(self):
        """Disconnect all active clients."""
        for client in self._clients.values():
            try:
                # ClaudeSDKClient handles cleanup via context manager
                pass
            except Exception as e:
                logger.error(f"Error disconnecting client: {e}")
        self._clients.clear()


# Global instance
agent_manager = AgentManager()
