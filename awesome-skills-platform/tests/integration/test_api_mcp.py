"""
Integration tests for MCP API endpoints.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestMCPEndpoints:
    """Tests for /api/mcp endpoints."""

    @patch("src.api.routers.mcp.db_client")
    def test_list_mcp_servers_empty(self, mock_db, test_client):
        """Test listing MCP servers when empty."""
        mock_db.list_mcp_servers.return_value = []

        response = test_client.get("/api/mcp")

        assert response.status_code == 200
        assert response.json() == []

    @patch("src.api.routers.mcp.db_client")
    def test_list_mcp_servers(self, mock_db, test_client):
        """Test listing MCP servers."""
        mock_db.list_mcp_servers.return_value = [
            {
                "id": "mcp-1",
                "name": "Calculator MCP",
                "connectionType": "http",
                "endpoint": "http://localhost:8080/",
                "config": {},
                "status": "online",
            },
            {
                "id": "mcp-2",
                "name": "GitHub MCP",
                "connectionType": "stdio",
                "endpoint": "npx @mcp/github",
                "config": {},
                "status": "offline",
            },
        ]

        response = test_client.get("/api/mcp")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Calculator MCP"
        assert data[1]["name"] == "GitHub MCP"

    @patch("src.api.routers.mcp.db_client")
    def test_get_mcp_server_success(self, mock_db, test_client):
        """Test getting a specific MCP server."""
        mock_db.get_mcp_server.return_value = {
            "id": "mcp-123",
            "name": "Test MCP",
            "connectionType": "http",
            "endpoint": "http://localhost:8080/",
            "config": {},
            "status": "online",
        }

        response = test_client.get("/api/mcp/mcp-123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "mcp-123"
        assert data["name"] == "Test MCP"

    @patch("src.api.routers.mcp.db_client")
    def test_get_mcp_server_not_found(self, mock_db, test_client):
        """Test getting non-existent MCP server."""
        mock_db.get_mcp_server.return_value = None

        response = test_client.get("/api/mcp/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch("src.api.routers.mcp.db_client")
    def test_create_mcp_server(self, mock_db, test_client):
        """Test creating a new MCP server."""
        mock_db.create_mcp_server.return_value = {
            "id": "new-mcp",
            "name": "New MCP Server",
            "connectionType": "http",
            "endpoint": "http://localhost:9000/",
            "config": {},
            "status": "offline",
        }

        response = test_client.post(
            "/api/mcp",
            json={
                "name": "New MCP Server",
                "connectionType": "http",
                "endpoint": "http://localhost:9000/",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New MCP Server"
        mock_db.create_mcp_server.assert_called_once()

    @patch("src.api.routers.mcp.db_client")
    def test_update_mcp_server(self, mock_db, test_client):
        """Test updating an MCP server."""
        mock_db.get_mcp_server.return_value = {
            "id": "update-mcp",
            "name": "Old Name",
            "connectionType": "http",
            "endpoint": "http://localhost:8080/",
            "config": {},
            "status": "offline",
        }
        mock_db.update_mcp_server.return_value = {
            "id": "update-mcp",
            "name": "Updated Name",
            "connectionType": "http",
            "endpoint": "http://localhost:9000/",
            "config": {},
            "status": "online",
        }

        response = test_client.put(
            "/api/mcp/update-mcp",
            json={
                "name": "Updated Name",
                "endpoint": "http://localhost:9000/",
                "status": "online",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["endpoint"] == "http://localhost:9000/"

    @patch("src.api.routers.mcp.db_client")
    def test_delete_mcp_server(self, mock_db, test_client):
        """Test deleting an MCP server."""
        mock_db.get_mcp_server.return_value = {
            "id": "delete-mcp",
            "name": "To Delete",
            "connectionType": "http",
            "endpoint": "http://localhost:8080/",
            "config": {},
            "status": "offline",
        }
        mock_db.delete_mcp_server.return_value = True

        response = test_client.delete("/api/mcp/delete-mcp")

        assert response.status_code == 204
        mock_db.delete_mcp_server.assert_called_once_with("delete-mcp")

    @patch("src.api.routers.mcp.db_client")
    def test_delete_mcp_server_not_found(self, mock_db, test_client):
        """Test deleting non-existent MCP server."""
        mock_db.get_mcp_server.return_value = None

        response = test_client.delete("/api/mcp/nonexistent")

        assert response.status_code == 404


class TestMCPTestConnection:
    """Tests for MCP connection testing endpoint."""

    @patch("src.api.routers.mcp.mcp_manager")
    @patch("src.api.routers.mcp.db_client")
    def test_test_connection_success(self, mock_db, mock_mcp_manager, test_client):
        """Test successful connection test."""
        mock_db.get_mcp_server.return_value = {
            "id": "test-mcp",
            "name": "Test MCP",
            "connectionType": "http",
            "endpoint": "http://localhost:8080/",
            "config": {},
            "status": "offline",
        }
        mock_db.update_mcp_server.return_value = {
            "id": "test-mcp",
            "name": "Test MCP",
            "connectionType": "http",
            "endpoint": "http://localhost:8080/",
            "config": {},
            "status": "online",
        }

        mock_mcp_manager.test_mcp_connection.return_value = {
            "status": "online",
            "tool_count": 4,
            "tools": [
                {"name": "add", "description": "Add numbers"},
                {"name": "subtract", "description": "Subtract numbers"},
            ],
            "error": None,
        }

        response = test_client.post("/api/mcp/test-mcp/test")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["tool_count"] == 4

    @patch("src.api.routers.mcp.mcp_manager")
    @patch("src.api.routers.mcp.db_client")
    def test_test_connection_failure(self, mock_db, mock_mcp_manager, test_client):
        """Test failed connection test."""
        mock_db.get_mcp_server.return_value = {
            "id": "test-mcp",
            "name": "Test MCP",
            "connectionType": "http",
            "endpoint": "http://localhost:8080/",
            "config": {},
            "status": "online",
        }
        mock_db.update_mcp_server.return_value = {
            "id": "test-mcp",
            "name": "Test MCP",
            "connectionType": "http",
            "endpoint": "http://localhost:8080/",
            "config": {},
            "status": "error",
        }

        mock_mcp_manager.test_mcp_connection.return_value = {
            "status": "error",
            "tool_count": 0,
            "tools": [],
            "error": "Connection refused",
        }

        response = test_client.post("/api/mcp/test-mcp/test")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error"] == "Connection refused"

    @patch("src.api.routers.mcp.db_client")
    def test_test_connection_not_found(self, mock_db, test_client):
        """Test connection test for non-existent MCP server."""
        mock_db.get_mcp_server.return_value = None

        response = test_client.post("/api/mcp/nonexistent/test")

        assert response.status_code == 404
