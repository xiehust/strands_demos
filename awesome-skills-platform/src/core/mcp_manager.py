"""
MCP Manager for managing Model Context Protocol client connections.
"""
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp import MCPClient
from typing import Optional, Dict, List, Any
import logging

from src.database.dynamodb import db_client

logger = logging.getLogger(__name__)


class MCPManager:
    """Manages MCP client connections and lifecycle."""

    def __init__(self):
        """Initialize MCP manager."""
        self._mcp_clients: Dict[str, MCPClient] = {}
        self._mcp_tools_cache: Dict[str, List[Any]] = {}
        logger.info("🔌 MCP Manager initialized")

    def get_mcp_client(self, mcp_id: str) -> Optional[MCPClient]:
        """
        Get or create an MCP client for the given MCP server ID.

        Args:
            mcp_id: The MCP server ID from DynamoDB

        Returns:
            MCPClient instance or None if connection fails

        Raises:
            ValueError: If MCP server configuration is invalid
        """
        # Return cached client if exists
        if mcp_id in self._mcp_clients:
            logger.info(f"♻️ Using cached MCP client for {mcp_id}")
            return self._mcp_clients[mcp_id]

        # Load MCP server config from database
        mcp_config = db_client.get_mcp_server(mcp_id)
        if not mcp_config:
            logger.error(f"❌ MCP server {mcp_id} not found in database")
            raise ValueError(f"MCP server {mcp_id} not found")

        # Create MCP client based on connection type
        try:
            mcp_client = self._create_mcp_client(mcp_config)
            if mcp_client:
                self._mcp_clients[mcp_id] = mcp_client
                logger.info(f"✅ MCP client created for {mcp_config.get('name', mcp_id)}")
                return mcp_client
        except Exception as e:
            logger.error(f"💥 Failed to create MCP client for {mcp_id}: {e}")
            raise

        return None

    def _create_mcp_client(self, mcp_config: dict) -> Optional[MCPClient]:
        """
        Create an MCP client based on configuration.

        Args:
            mcp_config: MCP server configuration from DynamoDB

        Returns:
            MCPClient instance or None
        """
        connection_type = mcp_config.get("connectionType", mcp_config.get("connection_type"))
        endpoint = mcp_config.get("endpoint")
        config = mcp_config.get("config", {})
        mcp_name = mcp_config.get("name", "Unknown")

        logger.info(f"🔧 Creating MCP client: {mcp_name} ({connection_type})")

        try:
            if connection_type == "stdio":
                # Parse stdio command and args
                # Expected format: endpoint = "command arg1 arg2" or config has command/args
                command = config.get("command", endpoint.split()[0] if endpoint else "")
                args = config.get("args", endpoint.split()[1:] if endpoint and len(endpoint.split()) > 1 else [])

                logger.info(f"📡 stdio connection: {command} {' '.join(args)}")

                return MCPClient(lambda: stdio_client(
                    StdioServerParameters(
                        command=command,
                        args=args
                    )
                ))

            elif connection_type == "sse":
                # Server-Sent Events connection
                logger.info(f"📡 SSE connection: {endpoint}")
                return MCPClient(lambda: sse_client(endpoint))

            elif connection_type == "http":
                # Streamable HTTP connection
                logger.info(f"📡 HTTP connection: {endpoint}")
                headers = config.get("headers", {})
                return MCPClient(lambda: streamablehttp_client(
                    url=endpoint,
                    headers=headers if headers else None
                ))

            else:
                logger.error(f"❌ Unknown connection type: {connection_type}")
                raise ValueError(f"Unsupported connection type: {connection_type}")

        except Exception as e:
            logger.error(f"💥 Failed to create MCP client: {e}")
            raise

    def get_mcp_tools(self, mcp_id: str, use_cache: bool = True) -> List[Any]:
        """
        Get tools from an MCP server.

        Args:
            mcp_id: The MCP server ID
            use_cache: Whether to use cached tools

        Returns:
            List of tools from the MCP server
        """
        # Return cached tools if available and requested
        if use_cache and mcp_id in self._mcp_tools_cache:
            logger.info(f"♻️ Using cached tools for MCP {mcp_id}")
            return self._mcp_tools_cache[mcp_id]

        # Get MCP client
        mcp_client = self.get_mcp_client(mcp_id)
        if not mcp_client:
            logger.warning(f"⚠️ MCP client not available for {mcp_id}")
            return []

        try:
            # List tools using context manager
            logger.info(f"🔍 Discovering tools from MCP server {mcp_id}...")
            with mcp_client:
                tools = mcp_client.list_tools_sync()
                logger.info(f"✅ Found {len(tools)} tools from MCP server {mcp_id}")

                # Cache tools
                self._mcp_tools_cache[mcp_id] = tools
                return tools

        except Exception as e:
            logger.error(f"💥 Failed to list tools from MCP {mcp_id}: {e}")
            return []

    def test_mcp_connection(self, mcp_id: str) -> Dict[str, Any]:
        """
        Test connection to an MCP server.

        Args:
            mcp_id: The MCP server ID

        Returns:
            Dict with connection status and tool count
        """
        logger.info(f"🧪 Testing MCP connection for {mcp_id}")

        try:
            tools = self.get_mcp_tools(mcp_id, use_cache=False)

            result = {
                "status": "online",
                "tool_count": len(tools),
                "tools": [
                    {
                        "name": tool.name if hasattr(tool, 'name') else str(tool),
                        "description": tool.description if hasattr(tool, 'description') else ""
                    }
                    for tool in tools[:10]  # Limit to first 10 tools
                ],
                "error": None
            }

            logger.info(f"✅ MCP connection test passed: {len(tools)} tools available")
            return result

        except Exception as e:
            logger.error(f"❌ MCP connection test failed: {e}")
            return {
                "status": "error",
                "tool_count": 0,
                "tools": [],
                "error": str(e)
            }

    def clear_cache(self, mcp_id: Optional[str] = None):
        """
        Clear MCP client cache.

        Args:
            mcp_id: If provided, clear only this MCP. Otherwise clear all.
        """
        if mcp_id:
            self._mcp_clients.pop(mcp_id, None)
            self._mcp_tools_cache.pop(mcp_id, None)
            logger.info(f"Cleared cache for MCP {mcp_id}")
        else:
            self._mcp_clients.clear()
            self._mcp_tools_cache.clear()
            logger.info("Cleared all MCP caches")


# Global MCP manager instance
mcp_manager = MCPManager()
