"""
Unit tests for MCP Manager.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestMCPManager:
    """Tests for MCPManager class."""

    def test_init(self):
        """Test MCPManager initialization."""
        from src.core.mcp_manager import MCPManager

        manager = MCPManager()
        assert manager._mcp_clients == {}
        assert manager._mcp_tools_cache == {}

    @patch("src.core.mcp_manager.db_client")
    def test_get_mcp_client_not_found(self, mock_db):
        """Test get_mcp_client with non-existent MCP server."""
        mock_db.get_mcp_server.return_value = None

        from src.core.mcp_manager import MCPManager

        manager = MCPManager()

        with pytest.raises(ValueError, match="not found"):
            manager.get_mcp_client("nonexistent-mcp")

    @patch("src.core.mcp_manager.db_client")
    @patch("src.core.mcp_manager.MCPClient")
    @patch("src.core.mcp_manager.streamablehttp_client")
    def test_get_mcp_client_http(self, mock_http_client, mock_mcp_client, mock_db):
        """Test get_mcp_client with HTTP connection type."""
        mock_db.get_mcp_server.return_value = {
            "id": "test-mcp",
            "name": "Test MCP",
            "connectionType": "http",
            "endpoint": "http://localhost:8080/mcp/",
            "config": {},
        }

        mock_client_instance = MagicMock()
        mock_mcp_client.return_value = mock_client_instance

        from src.core.mcp_manager import MCPManager

        manager = MCPManager()
        result = manager.get_mcp_client("test-mcp")

        assert result == mock_client_instance
        mock_mcp_client.assert_called_once()

    @patch("src.core.mcp_manager.db_client")
    @patch("src.core.mcp_manager.MCPClient")
    @patch("src.core.mcp_manager.sse_client")
    def test_get_mcp_client_sse(self, mock_sse_client, mock_mcp_client, mock_db):
        """Test get_mcp_client with SSE connection type."""
        mock_db.get_mcp_server.return_value = {
            "id": "sse-mcp",
            "name": "SSE MCP",
            "connectionType": "sse",
            "endpoint": "http://localhost:8080/sse/",
            "config": {},
        }

        mock_client_instance = MagicMock()
        mock_mcp_client.return_value = mock_client_instance

        from src.core.mcp_manager import MCPManager

        manager = MCPManager()
        result = manager.get_mcp_client("sse-mcp")

        assert result == mock_client_instance

    @patch("src.core.mcp_manager.db_client")
    @patch("src.core.mcp_manager.MCPClient")
    @patch("src.core.mcp_manager.stdio_client")
    def test_get_mcp_client_stdio(self, mock_stdio_client, mock_mcp_client, mock_db):
        """Test get_mcp_client with stdio connection type."""
        mock_db.get_mcp_server.return_value = {
            "id": "stdio-mcp",
            "name": "Stdio MCP",
            "connectionType": "stdio",
            "endpoint": "python script.py",
            "config": {"command": "python", "args": ["script.py"]},
        }

        mock_client_instance = MagicMock()
        mock_mcp_client.return_value = mock_client_instance

        from src.core.mcp_manager import MCPManager

        manager = MCPManager()
        result = manager.get_mcp_client("stdio-mcp")

        assert result == mock_client_instance

    @patch("src.core.mcp_manager.db_client")
    def test_get_mcp_client_unknown_type(self, mock_db):
        """Test get_mcp_client with unknown connection type."""
        mock_db.get_mcp_server.return_value = {
            "id": "unknown-mcp",
            "name": "Unknown MCP",
            "connectionType": "unknown",
            "endpoint": "http://localhost/",
            "config": {},
        }

        from src.core.mcp_manager import MCPManager

        manager = MCPManager()

        with pytest.raises(ValueError, match="Unsupported connection type"):
            manager.get_mcp_client("unknown-mcp")

    @patch("src.core.mcp_manager.db_client")
    @patch("src.core.mcp_manager.MCPClient")
    def test_get_mcp_client_cached(self, mock_mcp_client, mock_db):
        """Test get_mcp_client returns cached client."""
        from src.core.mcp_manager import MCPManager

        manager = MCPManager()

        # Pre-populate cache
        cached_client = MagicMock()
        manager._mcp_clients["cached-mcp"] = cached_client

        result = manager.get_mcp_client("cached-mcp")

        assert result == cached_client
        # Should not query database for cached client
        mock_db.get_mcp_server.assert_not_called()


class TestMCPManagerGetTools:
    """Tests for get_mcp_tools method."""

    @patch("src.core.mcp_manager.db_client")
    @patch("src.core.mcp_manager.MCPClient")
    @patch("src.core.mcp_manager.streamablehttp_client")
    def test_get_mcp_tools_success(self, mock_http, mock_mcp_client, mock_db):
        """Test successful tool discovery."""
        mock_db.get_mcp_server.return_value = {
            "id": "test-mcp",
            "connectionType": "http",
            "endpoint": "http://localhost:8080/",
            "config": {},
        }

        # Create mock tools
        mock_tool1 = MagicMock()
        mock_tool1.name = "add"
        mock_tool1.description = "Add numbers"

        mock_tool2 = MagicMock()
        mock_tool2.name = "subtract"
        mock_tool2.description = "Subtract numbers"

        # Setup MCP client mock
        mock_client = MagicMock()
        mock_client.list_tools_sync.return_value = [mock_tool1, mock_tool2]
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_mcp_client.return_value = mock_client

        from src.core.mcp_manager import MCPManager

        manager = MCPManager()
        tools = manager.get_mcp_tools("test-mcp", use_cache=False)

        assert len(tools) == 2
        assert tools[0].name == "add"

    def test_get_mcp_tools_from_cache(self):
        """Test get_mcp_tools returns cached tools."""
        from src.core.mcp_manager import MCPManager

        manager = MCPManager()

        # Pre-populate cache
        cached_tools = [MagicMock(name="cached_tool")]
        manager._mcp_tools_cache["cached-mcp"] = cached_tools

        result = manager.get_mcp_tools("cached-mcp", use_cache=True)

        assert result == cached_tools


class TestMCPManagerTestConnection:
    """Tests for test_mcp_connection method."""

    @patch("src.core.mcp_manager.db_client")
    @patch("src.core.mcp_manager.MCPClient")
    @patch("src.core.mcp_manager.streamablehttp_client")
    def test_connection_success(self, mock_http, mock_mcp_client, mock_db):
        """Test successful connection test."""
        mock_db.get_mcp_server.return_value = {
            "id": "test-mcp",
            "connectionType": "http",
            "endpoint": "http://localhost:8080/",
            "config": {},
        }

        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.description = "A test tool"

        mock_client = MagicMock()
        mock_client.list_tools_sync.return_value = [mock_tool]
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_mcp_client.return_value = mock_client

        from src.core.mcp_manager import MCPManager

        manager = MCPManager()
        result = manager.test_mcp_connection("test-mcp")

        assert result["status"] == "online"
        assert result["tool_count"] == 1
        assert result["error"] is None

    @patch("src.core.mcp_manager.db_client")
    def test_connection_failure(self, mock_db):
        """Test connection test failure."""
        mock_db.get_mcp_server.return_value = None

        from src.core.mcp_manager import MCPManager

        manager = MCPManager()
        result = manager.test_mcp_connection("nonexistent-mcp")

        assert result["status"] == "error"
        assert result["tool_count"] == 0
        assert result["error"] is not None


class TestMCPManagerClearCache:
    """Tests for clear_cache method."""

    def test_clear_specific_cache(self):
        """Test clearing specific MCP cache."""
        from src.core.mcp_manager import MCPManager

        manager = MCPManager()
        manager._mcp_clients = {"mcp1": MagicMock(), "mcp2": MagicMock()}
        manager._mcp_tools_cache = {"mcp1": [], "mcp2": []}

        manager.clear_cache("mcp1")

        assert "mcp1" not in manager._mcp_clients
        assert "mcp1" not in manager._mcp_tools_cache
        assert "mcp2" in manager._mcp_clients

    def test_clear_all_cache(self):
        """Test clearing all MCP caches."""
        from src.core.mcp_manager import MCPManager

        manager = MCPManager()
        manager._mcp_clients = {"mcp1": MagicMock(), "mcp2": MagicMock()}
        manager._mcp_tools_cache = {"mcp1": [], "mcp2": []}

        manager.clear_cache()

        assert manager._mcp_clients == {}
        assert manager._mcp_tools_cache == {}
