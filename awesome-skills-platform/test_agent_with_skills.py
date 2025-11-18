"""
Test script to verify skill integration with agent_manager.py
"""
import asyncio
import sys
import os
from decimal import Decimal

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.agent_manager import agent_manager
from src.database.dynamodb import db_client


async def test_agent_with_skills():
    """Test creating an agent with skills and running a conversation."""

    print("=" * 80)
    print("🧪 Testing Agent with Skills Integration")
    print("=" * 80)

    # Step 1: Create a test agent with skills in DynamoDB
    print("\n📝 Step 1: Creating test agent configuration in DynamoDB...")

    test_agent_config = {
        "id": "test-agent-skills",
        "name": "Test Agent with Skills",
        "modelId": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "temperature": Decimal("0.7"),
        "maxTokens": 4096,
        "thinkingEnabled": False,
        "thinkingBudget": 1024,
        "systemPrompt": "You are a helpful AI assistant with access to various skills. When asked to perform tasks that require specialized tools, use the appropriate skill.",
        "skillIds": ["xlsx", "docx", "pdf"],  # Enable multiple skills
        "mcpIds": [],
        "status": "active"
    }

    try:
        # Create agent in DynamoDB
        db_client.create_agent(test_agent_config)
        print(f"✅ Test agent created: {test_agent_config['id']}")
        print(f"   Skills enabled: {test_agent_config['skillIds']}")
    except Exception as e:
        print(f"⚠️ Agent might already exist: {e}")

    # Step 2: Load agent from agent_manager
    print("\n🤖 Step 2: Loading agent with skills from agent_manager...")

    try:
        agent = agent_manager.get_or_create_agent("test-agent-skills")
        print(f"✅ Agent loaded successfully")
        print(f"   Agent ID: {agent.agent_id}")

        # Note: Agent object doesn't expose tools/hooks attributes directly
        # They are configured internally during initialization
    except Exception as e:
        print(f"❌ Failed to load agent: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 3: Test basic conversation (without skill invocation)
    print("\n💬 Step 3: Testing basic conversation...")

    try:
        result = await agent_manager.run_async(
            agent_id="test-agent-skills",
            user_message="Hello! Can you tell me what skills you have access to?"
        )

        print(f"✅ Conversation successful")
        print(f"   Response: {result['message'][:200]}...")
        if result.get('thinking'):
            print(f"   Thinking blocks: {len(result['thinking'])}")
    except Exception as e:
        print(f"❌ Conversation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 4: Test skill invocation (ask agent to use xlsx skill)
    print("\n🎯 Step 4: Testing skill invocation...")

    try:
        result = await agent_manager.run_async(
            agent_id="test-agent-skills",
            user_message="I need to work with an Excel file. Can you invoke the xlsx skill to see what it can do?"
        )

        print(f"✅ Skill invocation test completed")
        print(f"   Response: {result['message'][:300]}...")
        print(f"   Model: {result['model_id']}")
        print(f"   Stop reason: {result.get('stop_reason')}")
    except Exception as e:
        print(f"❌ Skill invocation failed: {e}")
        import traceback
        traceback.print_exc()

    # Step 5: Cleanup
    print("\n🧹 Step 5: Cleanup...")
    try:
        # Clear agent cache
        agent_manager.clear_cache("test-agent-skills")
        print("✅ Agent cache cleared")

        # Optionally delete test agent from DynamoDB
        # db_client.delete_agent("test-agent-skills")
        # print("✅ Test agent deleted from DynamoDB")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

    print("\n" + "=" * 80)
    print("🎉 Test completed!")
    print("=" * 80)


async def test_agent_without_skills():
    """Test creating an agent without skills."""

    print("\n" + "=" * 80)
    print("🧪 Testing Agent WITHOUT Skills")
    print("=" * 80)

    test_agent_config = {
        "id": "test-agent-no-skills",
        "name": "Test Agent without Skills",
        "modelId": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "temperature": Decimal("0.7"),
        "maxTokens": 4096,
        "systemPrompt": "You are a helpful AI assistant.",
        "skillIds": [],  # No skills
        "mcpIds": [],
        "status": "active"
    }

    try:
        db_client.create_agent(test_agent_config)
        print(f"✅ Test agent (no skills) created")
    except Exception as e:
        print(f"⚠️ Agent might already exist: {e}")

    try:
        agent = agent_manager.get_or_create_agent("test-agent-no-skills")
        print(f"✅ Agent loaded successfully")
        print(f"   Agent ID: {agent.agent_id}")

        result = await agent_manager.run_async(
            agent_id="test-agent-no-skills",
            user_message="Hello! Tell me a short joke."
        )

        print(f"✅ Conversation successful")
        print(f"   Response: {result['message']}")

        agent_manager.clear_cache("test-agent-no-skills")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting Agent Skills Integration Tests\n")

    # Run tests
    asyncio.run(test_agent_without_skills())
    asyncio.run(test_agent_with_skills())

    print("\n✅ All tests completed!\n")
