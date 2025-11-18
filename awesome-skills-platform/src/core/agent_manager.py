"""
Agent manager for creating and managing Strands Agents with Bedrock models.
"""
from strands import Agent
from strands.models import BedrockModel
from typing import Optional, List
import logging

from src.database.dynamodb import db_client
from src.skill_tool import generate_skill_tool, SkillToolInterceptor

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages agent lifecycle and interactions."""

    def __init__(self):
        """Initialize agent manager."""
        self._agents: dict[str, Agent] = {}
        self._models: dict[str, BedrockModel] = {}
        self._skill_tool = None  # Lazy load skill tool
        self._skill_interceptor = None  # Lazy load skill interceptor

    def get_or_create_agent(self, agent_id: str) -> Agent:
        """
        Get an existing agent from cache or create a new one from database config.

        Args:
            agent_id: The agent ID to retrieve

        Returns:
            Agent: The configured Strands Agent

        Raises:
            ValueError: If agent not found in database
        """
        # Return cached agent if exists
        if agent_id in self._agents:
            return self._agents[agent_id]["agent"]

        # Load agent config from database
        agent_config = db_client.get_agent(agent_id)
        if not agent_config:
            raise ValueError(f"Agent {agent_id} not found")

        # Create agent
        agent = self._create_agent_from_config(agent_config)

        # Cache agent with model_id
        model_id = agent_config.get("modelId", agent_config.get("model_id"))
        self._agents[agent_id] = {"agent": agent, "model_id": model_id}

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
        thinking_enabled = config.get("thinkingEnabled", config.get("thinking_enabled", False))
        skill_ids = config.get("skillIds", config.get("skill_ids", []))

        # Prepare tools and hooks
        tools = []
        hooks = []

        # Load skills if enabled
        if skill_ids:
            logger.info(f"Agent {agent_id} has {len(skill_ids)} skills enabled: {skill_ids}")
            skill_tool = self._get_or_create_skill_tool()
            if skill_tool:
                tools.append(skill_tool)
                logger.info(f"✅ Skill tool added to agent {agent_id}")

                # Add skill interceptor to hooks
                if self._skill_interceptor:
                    hooks.append(self._skill_interceptor)
                    logger.info(f"✅ Skill interceptor added to agent {agent_id} hooks")
            else:
                logger.warning(f"⚠️ Skill tool not available for agent {agent_id}")

        # Create agent with configuration
        agent = Agent(
            model=model,
            system_prompt=system_prompt or "You are a helpful AI assistant.",
            agent_id=agent_id,
            tools=tools if tools else None,
            hooks=hooks if hooks else None,
        )

        logger.info(f"Created agent {agent_id} with model {model_id}, {len(tools)} tools, and {len(hooks)} hooks")

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

        # Extract model configuration (convert Decimal to proper types)
        temperature = float(config.get("temperature", 0.7))
        max_tokens = int(config.get("maxTokens", config.get("max_tokens", 4096)))
        thinking_enabled = bool(config.get("thinkingEnabled", config.get("thinking_enabled", False)))
        thinking_budget = int(config.get("thinkingBudget", config.get("thinking_budget", 1024)))

        # Create BedrockModel
        # Note: Thinking mode configuration is handled through additional_args
        model_kwargs = {
            "model_id": model_id,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "cache_prompt": "default",  # Enable prompt caching
        }

        # Add thinking configuration if enabled
        # TODO: Add thinking support when available in Strands SDK
        # if thinking_enabled:
        #     model_kwargs["additional_args"] = {
        #         "thinking": {
        #             "type": "enabled",
        #             "budget_tokens": thinking_budget
        #         }
        #     }

        model = BedrockModel(**model_kwargs)

        # Cache model along with model_id for later reference
        self._models[model_id] = {"model": model, "model_id": model_id}

        logger.info(f"Created model {model_id} (temp={temperature}, max_tokens={max_tokens}, thinking={thinking_enabled})")

        return model, model_id

    def _get_or_create_skill_tool(self):
        """
        Get or create the skill tool (lazy loading).

        Returns:
            The skill tool function, or None if skills are not available
        """
        if self._skill_tool is None:
            logger.info("🔧 Initializing skill system...")
            try:
                self._skill_tool = generate_skill_tool()
                if self._skill_tool:
                    # Also create the skill interceptor
                    self._skill_interceptor = SkillToolInterceptor()
                    logger.info("✅ Skill system initialized successfully")
                else:
                    logger.warning("⚠️ No skills found, skill system not available")
            except Exception as e:
                logger.error(f"❌ Failed to initialize skill system: {e}")
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
            self._agents.pop(agent_id, None)
            logger.info(f"Cleared cache for agent {agent_id}")
        else:
            self._agents.clear()
            self._models.clear()
            logger.info("Cleared all agent caches")

    async def run_async(self, agent_id: str, user_message: str) -> dict:
        """
        Run an asynchronous conversation with an agent.

        Args:
            agent_id: The agent ID to use
            user_message: The user's message

        Returns:
            dict: Response containing assistant message and metadata
        """
        agent = self.get_or_create_agent(agent_id)

        # Get model_id from cache
        model_id = self._agents[agent_id]["model_id"]

        # Run agent with user message
        result = await agent.invoke_async(user_message)

        # Extract response
        response_text = ""
        thinking_content = []

        # Try different parsing strategies
        # Strategy 1: Check for AgentResult.message attribute (Strands Agent standard)
        if hasattr(result, 'message') and result.message:
            # Check if message is a dict or string
            if isinstance(result.message, dict):
                # Extract content from dict structure
                content = result.message.get('content', [])
                if isinstance(content, list) and len(content) > 0:
                    # Extract text from content blocks
                    for block in content:
                        if isinstance(block, dict) and 'text' in block:
                            response_text += block['text']
                else:
                    response_text = str(content)
                logger.info(f"Parsed from result.message dict: {len(response_text)} chars")
            elif isinstance(result.message, str):
                response_text = result.message
                logger.info(f"Parsed from result.message string: {len(response_text)} chars")
            else:
                response_text = str(result.message)
                logger.info(f"Parsed from result.message (converted): {len(response_text)} chars")
        # Strategy 2: Check if result is a string (simple text response)
        elif isinstance(result, str):
            response_text = result
            logger.info("Parsed as string")
        # Strategy 3: Check for messages attribute
        elif hasattr(result, 'messages'):
            for message in result.messages:
                if message.role == "assistant":
                    for content in message.content:
                        if content.type == "text":
                            response_text += content.text
                        elif content.type == "thinking":
                            thinking_content.append(content.thinking)
            logger.info(f"Parsed from messages: {len(response_text)} chars")
        # Strategy 4: Check for content attribute
        elif hasattr(result, 'content'):
            if isinstance(result.content, str):
                response_text = result.content
            elif isinstance(result.content, list):
                for content in result.content:
                    if hasattr(content, 'type'):
                        if content.type == "text":
                            response_text += content.text
                        elif content.type == "thinking":
                            thinking_content.append(content.thinking)
            logger.info(f"Parsed from content: {len(response_text)} chars")
        # Strategy 5: Last resort - convert to string
        else:
            response_text = str(result)
            logger.warning(f"Using str() conversion: {len(response_text)} chars")

        return {
            "message": response_text,
            "thinking": thinking_content if thinking_content else None,
            "model_id": model_id,
            "stop_reason": result.stop_reason if hasattr(result, "stop_reason") else None,
        }


# Global agent manager instance
agent_manager = AgentManager()
