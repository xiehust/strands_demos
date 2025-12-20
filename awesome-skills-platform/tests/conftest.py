"""
Shared pytest fixtures for all tests.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Generator, Any

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# Environment Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables and singletons before each test."""
    # Store original env
    original_env = os.environ.copy()

    yield

    # Restore original env
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_aws_credentials():
    """Mock AWS credentials for testing."""
    with patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "testing",
        "AWS_SECRET_ACCESS_KEY": "testing",
        "AWS_SECURITY_TOKEN": "testing",
        "AWS_SESSION_TOKEN": "testing",
        "AWS_DEFAULT_REGION": "us-east-1",
    }):
        yield


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture
def mock_db_client():
    """Mock DynamoDB client."""
    with patch("src.database.dynamodb.db_client") as mock:
        yield mock


@pytest.fixture
def sample_agent_config():
    """Sample agent configuration from database."""
    return {
        "id": "test-agent-1",
        "name": "Test Agent",
        "modelId": "us.anthropic.claude-sonnet-4-5-20250514-v1:0",
        "temperature": 0.7,
        "maxTokens": 4096,
        "thinkingEnabled": False,
        "thinkingBudget": 1024,
        "systemPrompt": "You are a helpful test assistant.",
        "skillIds": [],
        "mcpIds": [],
        "status": "active",
    }


@pytest.fixture
def sample_agent_config_with_skills():
    """Sample agent configuration with skills enabled."""
    return {
        "id": "test-agent-2",
        "name": "Skilled Agent",
        "modelId": "us.anthropic.claude-sonnet-4-5-20250514-v1:0",
        "temperature": 0.7,
        "maxTokens": 4096,
        "thinkingEnabled": False,
        "thinkingBudget": 1024,
        "systemPrompt": "You are a helpful assistant with skills.",
        "skillIds": ["xlsx", "pdf"],
        "mcpIds": [],
        "status": "active",
    }


@pytest.fixture
def sample_agent_config_with_mcp():
    """Sample agent configuration with MCP servers."""
    return {
        "id": "test-agent-3",
        "name": "MCP Agent",
        "modelId": "us.anthropic.claude-sonnet-4-5-20250514-v1:0",
        "temperature": 0.7,
        "maxTokens": 4096,
        "thinkingEnabled": False,
        "thinkingBudget": 1024,
        "systemPrompt": "You are a helpful assistant with MCP tools.",
        "skillIds": [],
        "mcpIds": ["mcp-calculator"],
        "status": "active",
    }


@pytest.fixture
def sample_skill():
    """Sample skill metadata."""
    return {
        "id": "xlsx",
        "name": "xlsx",
        "description": "Excel file processing skill",
        "status": "active",
    }


@pytest.fixture
def sample_mcp_server():
    """Sample MCP server configuration."""
    return {
        "id": "mcp-calculator",
        "name": "Calculator MCP",
        "connectionType": "http",
        "endpoint": "http://localhost:8080/mcp/",
        "config": {},
        "status": "online",
    }


# =============================================================================
# Model and Agent Fixtures
# =============================================================================

@pytest.fixture
def mock_bedrock_model():
    """Mock Bedrock model."""
    mock = MagicMock()
    mock.model_id = "us.anthropic.claude-sonnet-4-5-20250514-v1:0"
    return mock


@pytest.fixture
def mock_agent():
    """Mock Strands Agent."""
    mock = MagicMock()
    mock.invoke_async = AsyncMock(return_value=MagicMock(
        message="Test response",
        stop_reason="end_turn",
    ))
    return mock


# =============================================================================
# MCP Fixtures
# =============================================================================

@pytest.fixture
def mock_mcp_client():
    """Mock MCP client."""
    mock = MagicMock()
    mock.list_tools_sync = MagicMock(return_value=[
        MagicMock(name="add", description="Add two numbers"),
        MagicMock(name="subtract", description="Subtract two numbers"),
    ])
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=False)
    return mock


# =============================================================================
# Memory Fixtures
# =============================================================================

@pytest.fixture
def mock_memory_manager():
    """Mock memory manager."""
    with patch("src.core.memory_manager.get_memory_manager") as mock:
        manager = MagicMock()
        manager.enabled = False
        manager.create_session_manager = MagicMock(return_value=None)
        mock.return_value = manager
        yield manager


@pytest.fixture
def mock_memory_manager_enabled():
    """Mock memory manager with memory enabled."""
    with patch("src.core.memory_manager.get_memory_manager") as mock:
        manager = MagicMock()
        manager.enabled = True
        manager.create_session_manager = MagicMock(return_value=MagicMock())
        mock.return_value = manager
        yield manager


# =============================================================================
# FastAPI Test Client Fixtures
# =============================================================================

@pytest.fixture
def test_client():
    """FastAPI test client."""
    from fastapi.testclient import TestClient
    from src.api.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_test_client():
    """Async FastAPI test client."""
    from httpx import AsyncClient, ASGITransport
    from src.api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


# =============================================================================
# Skill System Fixtures
# =============================================================================

@pytest.fixture
def mock_skill_tool():
    """Mock skill tool function."""
    def skill_func(command: str) -> str:
        return f"Launching skill: {command}"

    skill_func.__name__ = "Skill"
    skill_func.__doc__ = "Test skill tool"
    return skill_func


@pytest.fixture
def mock_skill_interceptor():
    """Mock skill tool interceptor."""
    mock = MagicMock()
    mock.register_hooks = MagicMock()
    return mock
