"""
Test script for AgentCore Memory integration.

This script tests that:
1. Memory manager initializes correctly (with or without AGENTCORE_MEMORY_ID)
2. Agents can be created with memory sessions
3. Conversations persist within a session
4. System gracefully handles missing AGENTCORE_MEMORY_ID

Note: Without AGENTCORE_MEMORY_ID set, memory is disabled but conversations still work.
"""

import asyncio
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_memory_integration():
    """Test AgentCore Memory integration."""

    # Import after setting up logging
    from src.core.memory_manager import get_memory_manager
    from src.core.agent_manager import agent_manager
    from src.database.dynamodb import db_client

    logger.info("=" * 80)
    logger.info("AgentCore Memory Integration Test")
    logger.info("=" * 80)

    # Test 1: Memory Manager Initialization
    logger.info("\n📋 Test 1: Memory Manager Initialization")
    logger.info("-" * 80)

    memory_manager = get_memory_manager()

    if memory_manager.is_enabled():
        logger.info("✅ Memory manager is ENABLED (AGENTCORE_MEMORY_ID is set)")
        logger.info(f"   Memory ID: {memory_manager.memory_id[:8]}...")
    else:
        logger.info("⚠️  Memory manager is DISABLED (AGENTCORE_MEMORY_ID not set)")
        logger.info("   Conversations will work but won't persist across sessions")

    # Test 2: Get available agents
    logger.info("\n📋 Test 2: Loading available agents")
    logger.info("-" * 80)

    agents = db_client.list_agents()
    if not agents:
        logger.error("❌ No agents found in database. Please create an agent first.")
        return

    test_agent_id = agents[0]["id"]
    test_agent_name = agents[0]["name"]
    logger.info(f"✅ Found {len(agents)} agents in database")
    logger.info(f"   Using agent: {test_agent_name} (ID: {test_agent_id})")

    # Test 3: Create agent WITH memory session
    logger.info("\n📋 Test 3: Creating agent WITH memory session")
    logger.info("-" * 80)

    session_id_1 = "test-session-001"
    actor_id = "test-user"

    try:
        agent_with_memory = agent_manager.get_or_create_agent(
            agent_id=test_agent_id,
            session_id=session_id_1,
            actor_id=actor_id
        )
        logger.info(f"✅ Agent created successfully with session: {session_id_1}")

        # Test conversation with memory
        logger.info("\n💬 Testing conversation 1...")
        result1 = await agent_manager.run_async(
            agent_id=test_agent_id,
            user_message="Hello! My name is Alice and I love programming.",
            session_id=session_id_1,
            actor_id=actor_id
        )
        logger.info(f"✅ Response 1: {result1['message'][:100]}...")

        # Test second message in same session
        logger.info("\n💬 Testing conversation 2 (same session)...")
        result2 = await agent_manager.run_async(
            agent_id=test_agent_id,
            user_message="What's my name and what do I love?",
            session_id=session_id_1,
            actor_id=actor_id
        )
        logger.info(f"✅ Response 2: {result2['message'][:150]}...")

        # Check if agent remembers (only if memory is enabled)
        if memory_manager.is_enabled():
            remembers_name = "alice" in result2['message'].lower()
            remembers_interest = "programming" in result2['message'].lower()

            if remembers_name and remembers_interest:
                logger.info("✅ SUCCESS: Agent remembers previous conversation!")
            else:
                logger.warning("⚠️  Agent might not remember (check response above)")
        else:
            logger.info("ℹ️  Memory disabled - agent won't remember across API calls")
            logger.info("   (This is expected when AGENTCORE_MEMORY_ID is not set)")

    except Exception as e:
        logger.error(f"❌ Error during memory test: {e}")
        import traceback
        traceback.print_exc()

    # Test 4: Create agent WITHOUT memory session
    logger.info("\n📋 Test 4: Creating agent WITHOUT memory session")
    logger.info("-" * 80)

    try:
        agent_without_memory = agent_manager.get_or_create_agent(
            agent_id=test_agent_id,
            session_id=None,  # No session ID
        )
        logger.info("✅ Agent created successfully without memory session")

        result3 = await agent_manager.run_async(
            agent_id=test_agent_id,
            user_message="Tell me a joke about Python programming.",
            session_id=None,  # No memory
        )
        logger.info(f"✅ Response (no memory): {result3['message'][:100]}...")

    except Exception as e:
        logger.error(f"❌ Error during no-memory test: {e}")

    # Test 5: Different session (should not remember previous conversation)
    logger.info("\n📋 Test 5: Testing different session (should not remember)")
    logger.info("-" * 80)

    session_id_2 = "test-session-002"

    try:
        result4 = await agent_manager.run_async(
            agent_id=test_agent_id,
            user_message="What's my name?",
            session_id=session_id_2,  # Different session
            actor_id=actor_id
        )
        logger.info(f"✅ Response from new session: {result4['message'][:100]}...")

        if memory_manager.is_enabled():
            if "alice" not in result4['message'].lower():
                logger.info("✅ SUCCESS: New session doesn't remember old conversation")
            else:
                logger.warning("⚠️  Unexpected: new session might be bleeding info")

    except Exception as e:
        logger.error(f"❌ Error during different session test: {e}")

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("Test Summary")
    logger.info("=" * 80)
    logger.info(f"Memory Status: {'ENABLED' if memory_manager.is_enabled() else 'DISABLED'}")
    logger.info(f"Agents Tested: {test_agent_name}")
    logger.info(f"Sessions Tested: {session_id_1}, {session_id_2}, None")

    if memory_manager.is_enabled():
        logger.info("\n✅ AgentCore Memory integration is ACTIVE")
        logger.info("   Conversations will persist within sessions")
    else:
        logger.info("\n⚠️  AgentCore Memory is DISABLED")
        logger.info("   To enable memory persistence, set AGENTCORE_MEMORY_ID environment variable")
        logger.info("   Example: export AGENTCORE_MEMORY_ID=your-memory-id")

    logger.info("\n🎉 Test completed!")


if __name__ == "__main__":
    asyncio.run(test_memory_integration())
