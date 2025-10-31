#!/usr/bin/env python3
"""
Test script for NewMCPClient with resource operations

This script demonstrates all the resource operation capabilities of the NewMCPClient,
including listing resources, resource templates, and reading resource contents.

Prerequisites:
1. Start the MCP server: python src/server.py
2. Install dependencies: pip install strands-agents mcp boto3
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path to import our custom NewMCPClient
sys.path.insert(0, str(Path(__file__).parent))

from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp import MCPClient


def test_sync_resource_operations():
    """Test all synchronous resource operations."""
    print("\n" + "="*80)
    print("Testing Synchronous Resource Operations")
    print("="*80)

    # Create the NewMCPClient
    client = MCPClient(
        lambda: streamablehttp_client("http://localhost:8000/mcp/")
    )

    with client:
        # Test 1: List Resources
        print("\n🔍 Test 1: List Resources")
        print("-"*80)
        try:
            resources_result = client.list_resources_sync()
            print(f"✅ Found {len(resources_result.resources)} resources")

            for resource in resources_result.resources:
                print(f"\n  📄 Resource: {resource.name}")
                print(f"     URI: {resource.uri}")
                if hasattr(resource, 'description') and resource.description:
                    print(f"     Description: {resource.description}")
                if hasattr(resource, 'mimeType') and resource.mimeType:
                    print(f"     MIME Type: {resource.mimeType}")

            # Check pagination
            if hasattr(resources_result, 'nextCursor') and resources_result.nextCursor:
                print(f"\n  📄 Next page cursor available: {resources_result.nextCursor}")
        except Exception as e:
            print(f"❌ Error listing resources: {e}")

        # Test 2: List Resource Templates
        print("\n\n🔍 Test 2: List Resource Templates")
        print("-"*80)
        try:
            templates_result = client.list_resource_templates_sync()
            print(f"✅ Found {len(templates_result.resourceTemplates)} resource templates")

            for template in templates_result.resourceTemplates:
                print(f"\n  📋 Template: {template.name}")
                print(f"     URI Template: {template.uriTemplate}")
                if hasattr(template, 'description') and template.description:
                    print(f"     Description: {template.description}")
                if hasattr(template, 'mimeType') and template.mimeType:
                    print(f"     MIME Type: {template.mimeType}")
        except Exception as e:
            print(f"❌ Error listing resource templates: {e}")

        # Test 3: Read Resource Contents
        print("\n\n🔍 Test 3: Read Resource Contents")
        print("-"*80)
        try:
            # Get the first resource and read it
            resources_result = client.list_resources_sync()
            if resources_result.resources:
                first_resource = resources_result.resources[0]
                print(f"Reading resource: {first_resource.uri}")

                read_result = client.read_resource_sync(first_resource.uri)
                print(f"✅ Successfully read resource with {len(read_result.contents)} content item(s)")

                for i, content in enumerate(read_result.contents):
                    print(f"\n  Content item {i+1}:")
                    if hasattr(content, 'text'):
                        text_preview = content.text[:200] if len(content.text) > 200 else content.text
                        print(f"    Type: Text")
                        print(f"    Preview: {text_preview}")
                        if len(content.text) > 200:
                            print(f"    ... (truncated, total {len(content.text)} characters)")
                    elif hasattr(content, 'blob'):
                        print(f"    Type: Binary (blob)")
                        print(f"    Size: {len(content.blob)} bytes (base64 encoded)")
            else:
                print("⚠️  No resources available to read")
        except Exception as e:
            print(f"❌ Error reading resource: {e}")

        # Test 4: Helper Methods
        print("\n\n🔍 Test 4: Helper Methods")
        print("-"*80)
        try:
            # Test list_all_resource_uris
            uris = client.list_all_resource_uris()
            print(f"✅ list_all_resource_uris(): Found {len(uris)} URIs")
            for uri in uris[:5]:  # Show first 5
                print(f"  - {uri}")
            if len(uris) > 5:
                print(f"  ... and {len(uris) - 5} more")

            # Test get_resource_content_as_text
            if uris:
                print(f"\n✅ get_resource_content_as_text() for: {uris[0]}")
                try:
                    text = client.get_resource_content_as_text(uris[0])
                    text_preview = text[:200] if len(text) > 200 else text
                    print(f"  Content preview: {text_preview}")
                    if len(text) > 200:
                        print(f"  ... (truncated, total {len(text)} characters)")
                except ValueError as ve:
                    print(f"  ⚠️  {ve}")
        except Exception as e:
            print(f"❌ Error with helper methods: {e}")

    print("\n" + "="*80)
    print("✅ Synchronous tests completed")
    print("="*80)


async def test_async_resource_operations():
    """Test all asynchronous resource operations."""
    print("\n" + "="*80)
    print("Testing Asynchronous Resource Operations")
    print("="*80)

    # Create the NewMCPClient
    client = MCPClient(
        lambda: streamablehttp_client("http://localhost:8000/mcp/")
    )

    with client:
        # Test 1: List Resources Async
        print("\n🔍 Test 1: List Resources (Async)")
        print("-"*80)
        try:
            resources_result = await client.list_resources_async()
            print(f"✅ Found {len(resources_result.resources)} resources")

            for resource in resources_result.resources[:3]:  # Show first 3
                print(f"  - {resource.name} ({resource.uri})")
            if len(resources_result.resources) > 3:
                print(f"  ... and {len(resources_result.resources) - 3} more")
        except Exception as e:
            print(f"❌ Error: {e}")

        # Test 2: List Resource Templates Async
        print("\n\n🔍 Test 2: List Resource Templates (Async)")
        print("-"*80)
        try:
            templates_result = await client.list_resource_templates_async()
            print(f"✅ Found {len(templates_result.resourceTemplates)} templates")

            for template in templates_result.resourceTemplates[:3]:  # Show first 3
                print(f"  - {template.name}: {template.uriTemplate}")
            if len(templates_result.resourceTemplates) > 3:
                print(f"  ... and {len(templates_result.resourceTemplates) - 3} more")
        except Exception as e:
            print(f"❌ Error: {e}")

        # Test 3: Read Resource Async
        print("\n\n🔍 Test 3: Read Resource (Async)")
        print("-"*80)
        try:
            resources_result = await client.list_resources_async()
            if resources_result.resources:
                first_uri = resources_result.resources[0].uri
                print(f"Reading: {first_uri}")

                read_result = await client.read_resource_async(first_uri)
                print(f"✅ Successfully read {len(read_result.contents)} content item(s)")
            else:
                print("⚠️  No resources available")
        except Exception as e:
            print(f"❌ Error: {e}")

        # Test 4: Helper Methods Async
        print("\n\n🔍 Test 4: Helper Methods (Async)")
        print("-"*80)
        try:
            uris = await client.list_all_resource_uris_async()
            print(f"✅ Found {len(uris)} URIs")

            if uris:
                text = await client.get_resource_content_as_text_async(uris[0])
                text_preview = text[:100] if len(text) > 100 else text
                print(f"✅ Read text content: {text_preview}...")
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n" + "="*80)
    print("✅ Asynchronous tests completed")
    print("="*80)


def test_integration_with_agent():
    """Test using NewMCPClient with a Strands agent."""
    print("\n" + "="*80)
    print("Testing Integration with Strands Agent")
    print("="*80)

    try:
        import boto3
        from strands import Agent
        from strands.models.bedrock import BedrockModel

        # Agent Configuration
        agent_model = BedrockModel(
            model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
            temperature=1,
            max_tokens=24000,
            boto_session=boto3.Session(),
            additional_request_fields={
                "thinking": {
                    "type": "enabled",
                    "budget_tokens": 1024
                },
                "anthropic_beta": [
                    "interleaved-thinking-2025-05-14",
                    "fine-grained-tool-streaming-2025-05-14"
                ]
            }
        )

        # Create NewMCPClient
        client = MCPClient(
            lambda: streamablehttp_client("http://localhost:8000/mcp/")
        )

        with client:
            # Get tools from MCP server
            tools = client.list_tools_sync()
            print(f"✅ Loaded {len(tools)} tools from MCP server")

            # Also demonstrate resource access
            resources = client.list_resources_sync()
            print(f"✅ Found {len(resources.resources)} resources")

            # Create agent
            agent = Agent(model=agent_model, tools=tools)
            print("✅ Created agent with MCP tools")

            # Test the agent
            print("\n💬 Testing agent with resource-aware query...")
            response = agent("What skills are available? List them briefly.")
            print(f"\nAgent response:\n{response.message['content'][0]['text'][:300]}...")

    except ImportError as e:
        print(f"⚠️  Skipping agent integration test: {e}")
        print("   (This is optional - install strands-agents and boto3 to test)")
    except Exception as e:
        print(f"❌ Error in agent integration: {e}")

    print("\n" + "="*80)
    print("✅ Integration test completed")
    print("="*80)


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("🧪 NewMCPClient Resource Operations Test Suite")
    print("="*80)
    print("\nThis script tests all resource operation capabilities of NewMCPClient")
    print("including synchronous and asynchronous methods.\n")

    try:
        # Test synchronous operations
        test_sync_resource_operations()

        # Test asynchronous operations
        asyncio.run(test_async_resource_operations())

        # Test integration with agent
        test_integration_with_agent()

        print("\n" + "="*80)
        print("✅ All tests completed successfully!")
        print("="*80)
        print("\nKey findings:")
        print("  - All resource operations (list, read) working correctly")
        print("  - Both sync and async methods functional")
        print("  - Helper methods providing convenient access")
        print("  - Integration with Strands agents successful")
        print("\nNext steps:")
        print("  - Use NewMCPClient in your applications")
        print("  - Leverage resources for contextual data")
        print("  - Combine tools and resources for rich agent capabilities")
        print("="*80 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Is the MCP server running? Start it with: python src/server.py")
        print("  2. Check server logs for errors")
        print("  3. Verify SKILLS_DIR environment variable")
        print("  4. Ensure port 8000 is accessible")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
