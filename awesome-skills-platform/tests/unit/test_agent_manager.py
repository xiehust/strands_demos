"""
Unit tests for Agent Manager.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestAgentManager:
    """Tests for AgentManager class."""

    def test_init(self):
        """Test AgentManager initialization."""
        from src.core.agent_manager import AgentManager

        manager = AgentManager()
        assert manager._agents == {}
        assert manager._models == {}
        assert manager._skill_tool is None
        assert manager._skill_interceptor is None


class TestAgentManagerGetOrCreateAgent:
    """Tests for get_or_create_agent method."""

    @patch("src.core.agent_manager.db_client")
    def test_agent_not_found(self, mock_db):
        """Test error when agent not found in database."""
        mock_db.get_agent.return_value = None

        from src.core.agent_manager import AgentManager

        manager = AgentManager()

        with pytest.raises(ValueError, match="not found"):
            manager.get_or_create_agent("nonexistent-agent")

    @patch("src.core.agent_manager.get_memory_manager")
    @patch("src.core.agent_manager.Agent")
    @patch("src.core.agent_manager.BedrockModel")
    @patch("src.core.agent_manager.db_client")
    def test_create_basic_agent(
        self, mock_db, mock_bedrock, mock_agent_class, mock_memory
    ):
        """Test creating a basic agent without skills or MCP."""
        mock_db.get_agent.return_value = {
            "id": "test-agent",
            "name": "Test Agent",
            "modelId": "us.anthropic.claude-sonnet-4-5-20250514-v1:0",
            "temperature": 0.7,
            "maxTokens": 4096,
            "thinkingEnabled": False,
            "systemPrompt": "You are helpful.",
            "skillIds": [],
            "mcpIds": [],
        }

        mock_model = MagicMock()
        mock_bedrock.return_value = mock_model

        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        mock_memory_manager = MagicMock()
        mock_memory_manager.create_session_manager.return_value = None
        mock_memory.return_value = mock_memory_manager

        from src.core.agent_manager import AgentManager

        manager = AgentManager()
        result = manager.get_or_create_agent("test-agent")

        assert result == mock_agent
        mock_bedrock.assert_called_once()
        mock_agent_class.assert_called_once()

    @patch("src.core.agent_manager.get_memory_manager")
    @patch("src.core.agent_manager.Agent")
    @patch("src.core.agent_manager.BedrockModel")
    @patch("src.core.agent_manager.db_client")
    def test_returns_cached_agent(
        self, mock_db, mock_bedrock, mock_agent_class, mock_memory
    ):
        """Test that cached agent is returned."""
        mock_db.get_agent.return_value = {
            "id": "cached-agent",
            "modelId": "claude-3",
            "temperature": 0.7,
            "maxTokens": 4096,
            "skillIds": [],
            "mcpIds": [],
        }

        mock_model = MagicMock()
        mock_bedrock.return_value = mock_model

        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        mock_memory_manager = MagicMock()
        mock_memory_manager.create_session_manager.return_value = None
        mock_memory.return_value = mock_memory_manager

        from src.core.agent_manager import AgentManager

        manager = AgentManager()

        # First call - creates agent
        result1 = manager.get_or_create_agent("cached-agent")

        # Second call - should return cached
        result2 = manager.get_or_create_agent("cached-agent")

        assert result1 == result2
        # Agent class should only be called once
        assert mock_agent_class.call_count == 1

    @patch("src.core.agent_manager.get_memory_manager")
    @patch("src.core.agent_manager.Agent")
    @patch("src.core.agent_manager.BedrockModel")
    @patch("src.core.agent_manager.db_client")
    def test_session_id_creates_separate_cache(
        self, mock_db, mock_bedrock, mock_agent_class, mock_memory
    ):
        """Test that different session IDs create separate cache entries."""
        mock_db.get_agent.return_value = {
            "id": "session-agent",
            "modelId": "claude-3",
            "temperature": 0.7,
            "maxTokens": 4096,
            "skillIds": [],
            "mcpIds": [],
        }

        mock_model = MagicMock()
        mock_bedrock.return_value = mock_model

        mock_agent_class.return_value = MagicMock()

        mock_memory_manager = MagicMock()
        mock_memory_manager.create_session_manager.return_value = MagicMock()
        mock_memory.return_value = mock_memory_manager

        from src.core.agent_manager import AgentManager

        manager = AgentManager()

        # Create with session 1
        manager.get_or_create_agent("session-agent", session_id="session-1")

        # Create with session 2 - should create new agent
        manager.get_or_create_agent("session-agent", session_id="session-2")

        # Should have created 2 agents (different sessions)
        assert mock_agent_class.call_count == 2


class TestAgentManagerWithSkills:
    """Tests for agent creation with skills."""

    @patch("src.core.agent_manager.generate_skill_tool")
    @patch("src.core.agent_manager.SkillToolInterceptor")
    @patch("src.core.agent_manager.get_memory_manager")
    @patch("src.core.agent_manager.Agent")
    @patch("src.core.agent_manager.BedrockModel")
    @patch("src.core.agent_manager.db_client")
    def test_agent_with_skills(
        self,
        mock_db,
        mock_bedrock,
        mock_agent_class,
        mock_memory,
        mock_interceptor_class,
        mock_gen_skill,
    ):
        """Test creating agent with skills enabled."""
        mock_db.get_agent.return_value = {
            "id": "skilled-agent",
            "modelId": "claude-3",
            "temperature": 0.7,
            "maxTokens": 4096,
            "skillIds": ["xlsx", "pdf"],
            "mcpIds": [],
        }

        mock_model = MagicMock()
        mock_bedrock.return_value = mock_model

        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        mock_memory_manager = MagicMock()
        mock_memory_manager.create_session_manager.return_value = None
        mock_memory.return_value = mock_memory_manager

        mock_skill_tool = MagicMock()
        mock_gen_skill.return_value = mock_skill_tool

        mock_interceptor = MagicMock()
        mock_interceptor_class.return_value = mock_interceptor

        from src.core.agent_manager import AgentManager

        manager = AgentManager()
        result = manager.get_or_create_agent("skilled-agent")

        # Verify skill tool was generated
        mock_gen_skill.assert_called_once()

        # Verify agent was created with tools
        call_kwargs = mock_agent_class.call_args.kwargs
        assert mock_skill_tool in call_kwargs.get("tools", [])


class TestAgentManagerWithMCP:
    """Tests for agent creation with MCP servers."""

    @patch("src.core.agent_manager.mcp_manager")
    @patch("src.core.agent_manager.get_memory_manager")
    @patch("src.core.agent_manager.Agent")
    @patch("src.core.agent_manager.BedrockModel")
    @patch("src.core.agent_manager.db_client")
    def test_agent_with_mcp(
        self, mock_db, mock_bedrock, mock_agent_class, mock_memory, mock_mcp_manager
    ):
        """Test creating agent with MCP servers enabled."""
        mock_db.get_agent.return_value = {
            "id": "mcp-agent",
            "modelId": "claude-3",
            "temperature": 0.7,
            "maxTokens": 4096,
            "skillIds": [],
            "mcpIds": ["mcp-calculator"],
        }

        mock_model = MagicMock()
        mock_bedrock.return_value = mock_model

        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        mock_memory_manager = MagicMock()
        mock_memory_manager.create_session_manager.return_value = None
        mock_memory.return_value = mock_memory_manager

        mock_mcp_client = MagicMock()
        mock_mcp_manager.get_mcp_client.return_value = mock_mcp_client

        from src.core.agent_manager import AgentManager

        manager = AgentManager()
        result = manager.get_or_create_agent("mcp-agent")

        # Verify MCP client was requested
        mock_mcp_manager.get_mcp_client.assert_called_once_with("mcp-calculator")

        # Verify agent was created with MCP client in tools
        call_kwargs = mock_agent_class.call_args.kwargs
        assert mock_mcp_client in call_kwargs.get("tools", [])


class TestAgentManagerRunAsync:
    """Tests for run_async method."""

    @patch("src.core.agent_manager.get_memory_manager")
    @patch("src.core.agent_manager.Agent")
    @patch("src.core.agent_manager.BedrockModel")
    @patch("src.core.agent_manager.db_client")
    async def test_run_async_basic(
        self, mock_db, mock_bedrock, mock_agent_class, mock_memory
    ):
        """Test basic async execution."""
        mock_db.get_agent.return_value = {
            "id": "async-agent",
            "modelId": "claude-3",
            "temperature": 0.7,
            "maxTokens": 4096,
            "skillIds": [],
            "mcpIds": [],
        }

        mock_model = MagicMock()
        mock_bedrock.return_value = mock_model

        # Mock agent with async response
        mock_result = MagicMock()
        mock_result.message = "Hello, I am an assistant!"
        mock_result.stop_reason = "end_turn"

        mock_agent = MagicMock()
        mock_agent.invoke_async = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent

        mock_memory_manager = MagicMock()
        mock_memory_manager.create_session_manager.return_value = None
        mock_memory.return_value = mock_memory_manager

        from src.core.agent_manager import AgentManager

        manager = AgentManager()
        result = await manager.run_async("async-agent", "Hello!")

        assert result["message"] == "Hello, I am an assistant!"
        assert result["model_id"] == "claude-3"
        mock_agent.invoke_async.assert_called_once_with("Hello!")

    @patch("src.core.agent_manager.get_memory_manager")
    @patch("src.core.agent_manager.Agent")
    @patch("src.core.agent_manager.BedrockModel")
    @patch("src.core.agent_manager.db_client")
    async def test_run_async_with_dict_message(
        self, mock_db, mock_bedrock, mock_agent_class, mock_memory
    ):
        """Test async execution with dict message format."""
        mock_db.get_agent.return_value = {
            "id": "dict-agent",
            "modelId": "claude-3",
            "temperature": 0.7,
            "maxTokens": 4096,
            "skillIds": [],
            "mcpIds": [],
        }

        mock_model = MagicMock()
        mock_bedrock.return_value = mock_model

        # Mock result with dict message structure
        mock_result = MagicMock()
        mock_result.message = {
            "content": [{"text": "Response from dict format"}]
        }
        mock_result.stop_reason = "end_turn"

        mock_agent = MagicMock()
        mock_agent.invoke_async = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent

        mock_memory_manager = MagicMock()
        mock_memory_manager.create_session_manager.return_value = None
        mock_memory.return_value = mock_memory_manager

        from src.core.agent_manager import AgentManager

        manager = AgentManager()
        result = await manager.run_async("dict-agent", "Hello!")

        assert "Response from dict format" in result["message"]


class TestAgentManagerClearCache:
    """Tests for clear_cache method."""

    def test_clear_specific_agent(self):
        """Test clearing specific agent from cache."""
        from src.core.agent_manager import AgentManager

        manager = AgentManager()
        manager._agents = {
            "agent1": {"agent": MagicMock(), "model_id": "claude-3"},
            "agent2": {"agent": MagicMock(), "model_id": "claude-3"},
        }

        manager.clear_cache("agent1")

        assert "agent1" not in manager._agents
        assert "agent2" in manager._agents

    def test_clear_all_cache(self):
        """Test clearing all caches."""
        from src.core.agent_manager import AgentManager

        manager = AgentManager()
        manager._agents = {
            "agent1": {"agent": MagicMock(), "model_id": "claude-3"},
        }
        manager._models = {
            "claude-3": {"model": MagicMock(), "model_id": "claude-3"},
        }

        manager.clear_cache()

        assert manager._agents == {}
        assert manager._models == {}
