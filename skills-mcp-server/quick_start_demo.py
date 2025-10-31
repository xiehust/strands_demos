#!/usr/bin/env python3
"""
Quick Start Demo - Skills MCP Server with Strands Agent

A minimal example showing how to connect a Strands agent to the Skills MCP Server
using the NewMCPClient with resource operations support.

Perfect for getting started quickly!

Prerequisites:
1. Start the MCP server: python src/server.py
2. Install dependencies: pip install strands-agents mcp boto3
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path to import NewMCPClient
sys.path.insert(0, str(Path(__file__).parent))

import boto3
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.tools.mcp import MCPClient


# Agent Configuration
agent_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    temperature=1,
    max_tokens=24000,
    boto_session=boto3.Session(),
    # additional_request_fields={
    #     "thinking": {
    #         "type": "enabled",
    #         "budget_tokens": 1024
    #     },
    #     "anthropic_beta": ["interleaved-thinking-2025-05-14", "fine-grained-tool-streaming-2025-05-14"]
    # }
)


def get_skill_resource(client: MCPClient):
    """Display available resources with human-readable names."""
    print("\n📚 Step 1b: Discovering available resources...")
    print("-"*80)

    # List resources
    resources_response = client.list_resources_sync()
    print(f"✅ Found {len(resources_response.resources)} resources:\n")
    all_skills = None
    for resource in resources_response.resources:
        print(f"  📄 {resource.name}")
        print(f"     URI: {resource.uri}")
        if hasattr(resource, 'description') and resource.description:
            print(f"     Description: {resource.description}")
        if resource.name == "list_skills":
            source = client.read_resource_sync(resource.uri)
            all_skills = source.contents[0].text
            print(all_skills)
            break 
    return all_skills
    # List resource templates
    # templates_response = client.list_resource_templates_sync()
    # if templates_response.resourceTemplates:
    #     print(f"📋 Found {len(templates_response.resourceTemplates)} resource templates:\n")

    #     for template in templates_response.resourceTemplates:
    #         print(f"  🔗 {template.name}")
    #         print(f"     URI Template: {template.uriTemplate}")
    #         if hasattr(template, 'description') and template.description:
    #             print(f"     Description: {template.description}")



async def main():
    print("\n" + "="*80)
    print("🚀 Quick Start Demo - Skills MCP Server + Strands Agent")
    print("="*80)
    print("\nThis demo shows how to use NewMCPClient with resource operations\n")

    # Step 1: Create NewMCPClient (with resource support!)
    print("📡 Step 1a: Creating NewMCPClient with resource operations support...")
    mcp_client = MCPClient(
        lambda: streamablehttp_client("http://localhost:8000/mcp/")
    )
    print("✅ NewMCPClient created\n")

    # Step 2: Connect to the server and explore
    print("🔌 Step 2: Connecting to Skills MCP Server...")
    print("-"*80)

    with mcp_client:
        # Get tools
        tools = mcp_client.list_tools_sync()
        print(f"✅ Connected! Loaded {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.tool_name}")

        # Display resources using the new resource operations
        skills_desc = get_skill_resource(mcp_client)

        
        # Step 3: Create agent with MCP tools
        print("🤖 Step 3: Creating Strands agent...")
        print("-"*80)
        agent = Agent(
            model=agent_model,
            system_prompt = f"You are equipped with skills:\n{skills_desc}",
            tools=tools
        )
        print("✅ Agent created with MCP tools\n")

        # Step 4: Use the agent
        print("💬 Step 4: Testing agent with queries...")
        print("="*80)

        # Query 1: List skills
        print("\n🔍 Query 1: What skills are available?")
        print("-"*80)
        response = agent("List all available skills with a brief description of each")
        print(response.message['content'])

        # Query 2: Invoke a skill
        print("\n" + "-"*80)
        print("🔍 Query 2: Tell me about the PDF skill")
        print("-"*80)
        response = agent("Invoke the pdf skill and give me a summary of what it can do")
        print(response.message['content'])

        # Query 3: Explore skill files
        print("\n" + "-"*80)
        print("🔍 Query 3: What files are in the PDF skill directory?")
        print("-"*80)
        response = agent("What files are available in the pdf skill directory?")
        print(response.message['content'])

        # Bonus: Direct resource access
        print("\n" + "-"*80)
        print("🔍 Bonus: Direct resource access (bypassing agent)")
        print("-"*80)
        print("Demonstrating direct resource reading with NewMCPClient...")

    print("\n" + "="*80)
    print("✅ Demo completed successfully!")
    print("="*80)
    print("\nWhat you learned:")
    print("  ✓ How to create and use NewMCPClient with resource operations")
    print("  ✓ How to list and read MCP resources directly")
    print("  ✓ How to integrate MCP tools with a Strands agent")
    print("  ✓ How to query skills through the agent")
    print("  ✓ How to access resources without going through the agent")
    print("\nNext steps:")
    print("  - Try asking different questions about skills")
    print("  - Explore other skills (docx, pptx, xlsx, etc.)")
    print("  - Use resource operations for custom workflows")
    print("  - See demo_agent.py for more advanced examples")
    print("  - Read DEMO_README.md for detailed documentation")
    print("  - Check test_new_mcp_client.py for comprehensive resource operation tests")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Is the MCP server running? Start it with: python src/server.py")
        print("  2. Is strands-agents installed? Install with: pip install strands-agents mcp boto3")
        print("  3. Check server logs for errors")
        print("  4. Verify SKILLS_DIR environment variable is set correctly")
        import traceback
        traceback.print_exc()
        raise
