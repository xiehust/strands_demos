"""
Test script for MCP integration.
Creates a simple calculator MCP server and tests agent integration.
"""
import sys
import os
import asyncio
import threading
import time
import logging

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mcp.server import FastMCP
from database.dynamodb import db_client
from core.agent_manager import agent_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_calculator_mcp_server():
    """Create a simple calculator MCP server."""
    logger.info("🧮 Creating Calculator MCP Server...")

    mcp = FastMCP("Calculator Server")

    @mcp.tool(description="Add two numbers together")
    def add(x: int, y: int) -> int:
        """Add two numbers."""
        return x + y

    @mcp.tool(description="Subtract one number from another")
    def subtract(x: int, y: int) -> int:
        """Subtract y from x."""
        return x - y

    @mcp.tool(description="Multiply two numbers")
    def multiply(x: int, y: int) -> int:
        """Multiply two numbers."""
        return x * y

    @mcp.tool(description="Divide one number by another")
    def divide(x: float, y: float) -> float:
        """Divide x by y."""
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y

    logger.info("✅ Calculator MCP Server created with 4 tools")
    mcp.run(transport="streamable-http")


def start_mcp_server_background():
    """Start MCP server in background thread."""
    logger.info("🚀 Starting MCP server in background...")
    server_thread = threading.Thread(target=create_calculator_mcp_server, daemon=True)
    server_thread.start()
    time.sleep(3)  # Wait for server to start
    logger.info("✅ MCP server started on http://localhost:8000/mcp/")


def create_test_mcp_config():
    """Create a test MCP server configuration in DynamoDB."""
    logger.info("📝 Creating test MCP configuration in DynamoDB...")

    mcp_data = {
        "name": "Calculator MCP Server",
        "description": "A simple calculator MCP server for testing",
        "connectionType": "http",
        "endpoint": "http://localhost:8000/mcp/",
        "config": {},
        "status": "offline"
    }

    try:
        created_mcp = db_client.create_mcp_server(mcp_data)
        logger.info(f"✅ MCP configuration created with ID: {created_mcp['id']}")
        return created_mcp['id']
    except Exception as e:
        logger.error(f"❌ Failed to create MCP configuration: {e}")
        return None


def create_test_agent_with_mcp(mcp_id: str):
    """Create a test agent with MCP enabled."""
    logger.info("🤖 Creating test agent with MCP enabled...")

    agent_data = {
        "name": "MCP Test Agent",
        "description": "Agent for testing MCP integration",
        "modelId": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "temperature": 0.7,
        "maxTokens": 4096,
        "thinkingEnabled": False,
        "thinkingBudget": 1024,
        "systemPrompt": "You are a helpful assistant with access to calculator tools via MCP.",
        "skillIds": [],
        "mcpIds": [mcp_id],
        "status": "active"
    }

    try:
        created_agent = db_client.create_agent(agent_data)
        logger.info(f"✅ Test agent created with ID: {created_agent['id']}")
        return created_agent['id']
    except Exception as e:
        logger.error(f"❌ Failed to create test agent: {e}")
        return None


async def test_agent_with_mcp(agent_id: str):
    """Test agent with MCP tools."""
    logger.info("🧪 Testing agent with MCP tools...")
    logger.info("="*60)

    test_message = "Calculate 25 multiplied by 48"
    logger.info(f"User: {test_message}")
    logger.info("-"*60)

    try:
        result = await agent_manager.run_async(agent_id, test_message)
        logger.info(f"Agent: {result['message']}")
        logger.info("-"*60)
        logger.info(f"Model: {result['model_id']}")
        logger.info(f"Stop reason: {result['stop_reason']}")
        logger.info("="*60)
        logger.info("✅ MCP integration test completed successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ MCP integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup(mcp_id: str = None, agent_id: str = None):
    """Clean up test resources."""
    logger.info("🧹 Cleaning up test resources...")

    if agent_id:
        try:
            db_client.delete_agent(agent_id)
            logger.info(f"✅ Deleted test agent: {agent_id}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to delete test agent: {e}")

    if mcp_id:
        try:
            db_client.delete_mcp_server(mcp_id)
            logger.info(f"✅ Deleted test MCP: {mcp_id}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to delete test MCP: {e}")


async def main():
    """Run the MCP integration test."""
    logger.info("🚀 Starting MCP Integration Test")
    logger.info("="*60)

    mcp_id = None
    agent_id = None

    try:
        # Step 1: Start MCP server in background
        start_mcp_server_background()

        # Step 2: Create MCP configuration in DynamoDB
        mcp_id = create_test_mcp_config()
        if not mcp_id:
            logger.error("❌ Failed to create MCP configuration")
            return

        # Step 3: Test MCP connection
        from core.mcp_manager import mcp_manager
        logger.info("🔌 Testing MCP connection...")
        connection_result = mcp_manager.test_mcp_connection(mcp_id)
        logger.info(f"Connection status: {connection_result['status']}")
        logger.info(f"Tools found: {connection_result['tool_count']}")

        if connection_result['status'] != 'online':
            logger.error(f"❌ MCP connection failed: {connection_result.get('error')}")
            return

        # Step 4: Create test agent with MCP
        agent_id = create_test_agent_with_mcp(mcp_id)
        if not agent_id:
            logger.error("❌ Failed to create test agent")
            return

        # Step 5: Test agent with MCP tools
        success = await test_agent_with_mcp(agent_id)

        if success:
            logger.info("🎉 All tests passed!")
        else:
            logger.error("❌ Some tests failed")

    except KeyboardInterrupt:
        logger.info("⚠️ Test interrupted by user")
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        cleanup(mcp_id, agent_id)
        logger.info("✅ Test complete")


if __name__ == "__main__":
    asyncio.run(main())
