"""
Integration tests for Agent API endpoints.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


# Helper to create complete agent data
def make_agent_data(
    agent_id: str,
    name: str,
    model_id: str = "claude-3",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    thinking_enabled: bool = False,
    thinking_budget: int = 1024,
    skill_ids: list = None,
    mcp_ids: list = None,
    status: str = "active",
):
    """Create complete agent data with all required fields."""
    return {
        "id": agent_id,
        "name": name,
        "modelId": model_id,
        "temperature": temperature,
        "maxTokens": max_tokens,
        "thinkingEnabled": thinking_enabled,
        "thinkingBudget": thinking_budget,
        "skillIds": skill_ids or [],
        "mcpIds": mcp_ids or [],
        "status": status,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }


class TestAgentEndpoints:
    """Tests for /api/agents endpoints."""

    @patch("src.api.routers.agents.db_client")
    def test_list_agents_empty(self, mock_db, test_client):
        """Test listing agents when empty."""
        mock_db.list_agents.return_value = []

        response = test_client.get("/api/agents")

        assert response.status_code == 200
        assert response.json() == []

    @patch("src.api.routers.agents.db_client")
    def test_list_agents(self, mock_db, test_client):
        """Test listing agents."""
        mock_db.list_agents.return_value = [
            make_agent_data("agent-1", "Test Agent 1"),
            make_agent_data("agent-2", "Test Agent 2", temperature=0.5, max_tokens=2048,
                          thinking_enabled=True, thinking_budget=2048, skill_ids=["xlsx"]),
        ]

        response = test_client.get("/api/agents")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Test Agent 1"
        assert data[1]["name"] == "Test Agent 2"

    @patch("src.api.routers.agents.db_client")
    def test_get_agent_success(self, mock_db, test_client):
        """Test getting a specific agent."""
        mock_db.get_agent.return_value = make_agent_data("agent-123", "Specific Agent")

        response = test_client.get("/api/agents/agent-123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "agent-123"
        assert data["name"] == "Specific Agent"

    @patch("src.api.routers.agents.db_client")
    def test_get_agent_not_found(self, mock_db, test_client):
        """Test getting non-existent agent."""
        mock_db.get_agent.return_value = None

        response = test_client.get("/api/agents/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch("src.api.routers.agents.db_client")
    def test_create_agent(self, mock_db, test_client):
        """Test creating a new agent."""
        mock_db.create_agent.return_value = make_agent_data(
            "new-agent", "New Agent",
            model_id="us.anthropic.claude-sonnet-4-5-20250514-v1:0"
        )

        response = test_client.post(
            "/api/agents",
            json={
                "name": "New Agent",
                "modelId": "us.anthropic.claude-sonnet-4-5-20250514-v1:0",
                "temperature": 0.7,
                "maxTokens": 4096,
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Agent"
        mock_db.create_agent.assert_called_once()

    @patch("src.api.routers.agents.db_client")
    def test_update_agent(self, mock_db, test_client):
        """Test updating an agent."""
        mock_db.get_agent.return_value = make_agent_data("update-agent", "Old Name")
        mock_db.update_agent.return_value = make_agent_data(
            "update-agent", "Updated Name", temperature=0.8
        )

        response = test_client.put(
            "/api/agents/update-agent",
            json={
                "name": "Updated Name",
                "temperature": 0.8,
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["temperature"] == 0.8

    @patch("src.api.routers.agents.db_client")
    def test_update_agent_not_found(self, mock_db, test_client):
        """Test updating non-existent agent."""
        mock_db.get_agent.return_value = None

        response = test_client.put(
            "/api/agents/nonexistent",
            json={"name": "New Name"}
        )

        assert response.status_code == 404

    @patch("src.api.routers.agents.db_client")
    def test_delete_agent(self, mock_db, test_client):
        """Test deleting an agent."""
        mock_db.get_agent.return_value = make_agent_data("delete-agent", "To Delete")
        mock_db.delete_agent.return_value = True

        response = test_client.delete("/api/agents/delete-agent")

        assert response.status_code == 204
        mock_db.delete_agent.assert_called_once_with("delete-agent")

    @patch("src.api.routers.agents.db_client")
    def test_delete_agent_not_found(self, mock_db, test_client):
        """Test deleting non-existent agent."""
        mock_db.get_agent.return_value = None

        response = test_client.delete("/api/agents/nonexistent")

        assert response.status_code == 404
