"""
Agent manager for creating and managing Strands Agents with Bedrock models.

Simplified version - runs agents directly in the FastAPI backend without AgentCore Runtime.
"""
from strands import Agent
from strands.models import BedrockModel
from typing import Optional
import logging

from src.database.dynamodb import db_client
from src.skill_tool import generate_skill_tool, SkillToolInterceptor
from src.core.mcp_manager import mcp_manager
from src.core.memory_manager import get_memory_manager

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages agent lifecycle and interactions."""

    def __init__(self):
        """Initialize agent manager."""
        self._agents: dict[str, dict] = {}
        self._models: dict[str, dict] = {}
        self._skill_tool = None
        self._skill_interceptor = None

    def get_or_create_agent(
        self,
        agent_id: str,
        session_id: Optional[str] = None,
        actor_id: str = "default-user",
    ) -> Agent:
        """
        Get an existing agent from cache or create a new one from database config.

        Args:
            agent_id: The agent ID to retrieve
            session_id: Optional session ID for conversation tracking
            actor_id: User/actor identifier

        Returns:
            Agent: The configured Strands Agent

        Raises:
            ValueError: If agent not found in database
        """
        # Build cache key that includes session_id
        cache_key = f"{agent_id}:{session_id}" if session_id else agent_id

        # Return cached agent if exists
        if cache_key in self._agents:
            return self._agents[cache_key]["agent"]

        # Load agent config from database
        agent_config = db_client.get_agent(agent_id)
        if not agent_config:
            raise ValueError(f"Agent {agent_id} not found")

        # Create agent
        agent = self._create_agent_from_config(agent_config)

        # Cache agent with model_id
        model_id = agent_config.get("modelId", agent_config.get("model_id"))
        self._agents[cache_key] = {"agent": agent, "model_id": model_id}

        return agent

    def _create_agent_from_config(self, config: dict) -> Agent:
        """
        Create a Strands Agent from configuration.

        Args:
            config: Agent configuration dictionary

        Returns:
            Agent: Configured Strands Agent
        """
        agent_id = config.get("id")
        model_id = config.get("modelId", config.get("model_id"))

        # Get or create model
        model, _ = self._get_or_create_model(model_id, config)

        # Extract configuration
        system_prompt = config.get("systemPrompt", config.get("system_prompt"))
        skill_ids = config.get("skillIds", config.get("skill_ids", []))
        mcp_ids = config.get("mcpIds", config.get("mcp_ids", []))

        # Prepare tools and hooks
        tools = []
        hooks = []

        # Load skills if enabled
        if skill_ids:
            logger.info(f"Agent {agent_id} has {len(skill_ids)} skills enabled: {skill_ids}")
            skill_tool = self._get_or_create_skill_tool()
            if skill_tool:
                tools.append(skill_tool)
                logger.info(f"Skill tool added to agent {agent_id}")

                # Add skill interceptor to hooks
                if self._skill_interceptor:
                    hooks.append(self._skill_interceptor)
                    logger.info(f"Skill interceptor added to agent {agent_id} hooks")
            else:
                logger.warning(f"Skill tool not available for agent {agent_id}")

        # Load MCP clients if enabled
        if mcp_ids:
            logger.info(f"Agent {agent_id} has {len(mcp_ids)} MCP servers enabled: {mcp_ids}")
            for mcp_id in mcp_ids:
                try:
                    mcp_client = mcp_manager.get_mcp_client(mcp_id)
                    if mcp_client:
                        tools.append(mcp_client)
                        logger.info(f"Added MCP client for server {mcp_id}")
                    else:
                        logger.warning(f"Could not create MCP client for {mcp_id}")
                except Exception as e:
                    logger.error(f"Failed to load MCP client {mcp_id}: {e}")

        # Create agent (no session_manager - we handle memory manually)
        agent = Agent(
            model=model,
            system_prompt=system_prompt or "You are a helpful AI assistant.",
            agent_id=agent_id,
            tools=tools if tools else None,
            hooks=hooks if hooks else None,
        )

        logger.info(f"Created agent {agent_id} with model {model_id}, {len(tools)} tools")

        return agent

    def _get_or_create_model(self, model_id: str, config: dict) -> tuple[BedrockModel, str]:
        """
        Get or create a BedrockModel instance.

        Args:
            model_id: The Bedrock model ID
            config: Agent configuration with model parameters

        Returns:
            tuple: (BedrockModel, model_id)
        """
        # Return cached model if exists
        if model_id in self._models:
            cached = self._models[model_id]
            return cached["model"], cached["model_id"]

        # Extract model configuration
        temperature = float(config.get("temperature", 0.7))
        max_tokens = int(config.get("maxTokens", config.get("max_tokens", 4096)))

        # Create BedrockModel
        model_kwargs = {
            "model_id": model_id,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "cache_prompt": "default",  # Enable prompt caching
        }

        model = BedrockModel(**model_kwargs)

        # Cache model
        self._models[model_id] = {"model": model, "model_id": model_id}

        logger.info(f"Created model {model_id} (temp={temperature}, max_tokens={max_tokens})")

        return model, model_id

    def _get_or_create_skill_tool(self):
        """
        Get or create the skill tool (lazy loading).

        Returns:
            The skill tool function, or None if skills are not available
        """
        if self._skill_tool is None:
            logger.info("Initializing skill system...")
            try:
                self._skill_tool = generate_skill_tool()
                if self._skill_tool:
                    self._skill_interceptor = SkillToolInterceptor()
                    logger.info("Skill system initialized successfully")
                else:
                    logger.warning("No skills found, skill system not available")
            except Exception as e:
                logger.error(f"Failed to initialize skill system: {e}")
                self._skill_tool = None
                self._skill_interceptor = None

        return self._skill_tool

    def clear_cache(self, agent_id: Optional[str] = None):
        """
        Clear agent cache.

        Args:
            agent_id: If provided, clear only this agent. Otherwise clear all.
        """
        if agent_id:
            # Clear all cache keys that start with this agent_id
            keys_to_remove = [k for k in self._agents if k.startswith(f"{agent_id}:") or k == agent_id]
            for key in keys_to_remove:
                del self._agents[key]
            logger.info(f"Cleared cache for agent {agent_id}")
        else:
            self._agents.clear()
            self._models.clear()
            logger.info("Cleared all agent caches")

    async def run_async(
        self,
        agent_id: str,
        user_message: str,
        session_id: Optional[str] = None,
        actor_id: str = "default-user",
    ) -> dict:
        """
        Run an asynchronous conversation with an agent.

        Args:
            agent_id: The agent ID to use
            user_message: The user's message
            session_id: Optional session ID for conversation tracking
            actor_id: User/actor identifier

        Returns:
            dict: Response containing assistant message and metadata
        """
        agent = self.get_or_create_agent(agent_id, session_id=session_id, actor_id=actor_id)

        # Get model_id from cache
        cache_key = f"{agent_id}:{session_id}" if session_id else agent_id
        model_id = self._agents[cache_key]["model_id"]

        # Get or create conversation session for history tracking
        memory_manager = get_memory_manager()
        session = None
        if session_id:
            session = memory_manager.get_or_create_session(
                session_id=session_id,
                agent_id=agent_id,
                actor_id=actor_id,
            )
            # Add user message to history
            session.add_message("user", user_message)

        # Run agent with user message
        result = await agent.invoke_async(user_message)

        # Extract response text
        response_text = self._extract_response_text(result)

        # Save assistant response to history
        if session:
            session.add_message("assistant", response_text)

        return {
            "message": response_text,
            "thinking": None,
            "model_id": model_id,
            "stop_reason": result.stop_reason if hasattr(result, "stop_reason") else None,
        }

    def _extract_response_text(self, result) -> str:
        """
        Extract text from agent result using multiple strategies.

        Args:
            result: The agent result object

        Returns:
            str: Extracted response text
        """
        response_text = ""

        # Strategy 1: Check for AgentResult.message attribute
        if hasattr(result, 'message') and result.message:
            if isinstance(result.message, dict):
                content = result.message.get('content', [])
                if isinstance(content, list) and len(content) > 0:
                    for block in content:
                        if isinstance(block, dict) and 'text' in block:
                            response_text += block['text']
                else:
                    response_text = str(content)
            elif isinstance(result.message, str):
                response_text = result.message
            else:
                response_text = str(result.message)
        # Strategy 2: Check if result is a string
        elif isinstance(result, str):
            response_text = result
        # Strategy 3: Check for messages attribute
        elif hasattr(result, 'messages'):
            for message in result.messages:
                if message.role == "assistant":
                    for content in message.content:
                        if content.type == "text":
                            response_text += content.text
        # Strategy 4: Check for content attribute
        elif hasattr(result, 'content'):
            if isinstance(result.content, str):
                response_text = result.content
            elif isinstance(result.content, list):
                for content in result.content:
                    if hasattr(content, 'type') and content.type == "text":
                        response_text += content.text
        # Strategy 5: Last resort
        else:
            response_text = str(result)

        return response_text


# Global agent manager instance
agent_manager = AgentManager()
