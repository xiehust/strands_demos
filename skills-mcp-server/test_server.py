#!/usr/bin/env python3
"""
Test script for Skills MCP Server

This script demonstrates how to use the skills MCP server by testing all tools and resources.
"""

import asyncio
import os
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

# Set the skills directory
os.environ["SKILLS_DIR"] = "/home/ubuntu/workspace/strands_demos/strands_skills_demo/skills"


async def test_server():
    """Test the Skills MCP server functionality."""

    print("=" * 80)
    print("Testing Skills MCP Server")
    print("=" * 80)


    async with streamablehttp_client("http://localhost:8000/mcp") as (read, write,_):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            print("\n✓ Server initialized successfully\n")

            # Test 1: List all available tools
            print("-" * 80)
            print("TEST 1: List Tools")
            print("-" * 80)
            tools = await session.list_tools()
            print(f"Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tools}...")

            # Test 2: List all resources
            print("\n" + "-" * 80)
            print("TEST 2: List Resources")
            print("-" * 80)
            resources = await session.list_resources()
            print(f"Found {len(resources.resources)} resources:")
            for resource in resources.resources:
                print(f"  - {resource.uri}: {resource.name}")

            # Test 3: Read skills://list resource
            print("\n" + "-" * 80)
            print(f"TEST 3: Read {resource.uri} Resource")
            print("-" * 80)
            skills_list = await session.read_resource(resource.uri)
            print("Skills list (first 500 chars):")
            print(skills_list.contents[0].text[:500] + "...")

            # Test 4: Invoke a skill
            print("\n" + "-" * 80)
            print("TEST 4: Invoke 'pdf' Skill")
            print("-" * 80)
            result = await session.call_tool("invoke_skill", {"skill_name": "pdf"})
            print("Skill invoked successfully!")
            print(f"Result (first 500 chars):")
            if hasattr(result, 'content') and result.content:
                if hasattr(result.content[0], 'text'):
                    print(result.content[0].text[:500] + "...")
                else:
                    print(str(result.content[0])[:500] + "...")

            # Test 5: List skill files
            print("\n" + "-" * 80)
            print("TEST 5: List Files in 'pdf' Skill")
            print("-" * 80)
            files_result = await session.call_tool("list_skill_files", {
                "skill_name": "pdf",
                "subdirectory": ""
            })
            if hasattr(files_result, 'content') and files_result.content:
                if hasattr(files_result.content[0], 'text'):
                    print(files_result.content[0].text)
                else:
                    print(str(files_result.content[0]))

            # Test 6: Read a skill file
            print("\n" + "-" * 80)
            print("TEST 6: Read 'reference.md' from 'pdf' Skill")
            print("-" * 80)
            try:
                file_result = await session.call_tool("read_skill_file", {
                    "skill_name": "pdf",
                    "file_path": "reference.md"
                })
                print("File read successfully!")
                if hasattr(file_result, 'content') and file_result.content:
                    if hasattr(file_result.content[0], 'text'):
                        print(f"Content (first 300 chars): {file_result.content[0].text[:300]}...")
                    else:
                        print(f"Content (first 300 chars): {str(file_result.content[0])[:300]}...")
            except Exception as e:
                print(f"Note: File may not exist - {e}")

            # Test 7: Read a skill resource
            print("\n" + "-" * 80)
            print("TEST 7: Read 'skills://pdf' Resource")
            print("-" * 80)
            pdf_skill = await session.read_resource("skills://pdf")
            print("PDF skill resource (first 500 chars):")
            print(pdf_skill.contents[0].text[:500] + "...")

            # Test 8: Security test - try to read outside skill directory (should fail)
            print("\n" + "-" * 80)
            print("TEST 8: Security - Directory Traversal Prevention")
            print("-" * 80)
            try:
                bad_result = await session.call_tool("read_skill_file", {
                    "skill_name": "pdf",
                    "file_path": "../../../etc/passwd"
                })
                if hasattr(bad_result, 'content') and bad_result.content:
                    if hasattr(bad_result.content[0], 'text'):
                        content = bad_result.content[0].text
                    else:
                        content = str(bad_result.content[0])
                    if "Access denied" in content or "Error" in content:
                        print("✓ Security test passed - directory traversal blocked")
                    else:
                        print("✗ Security test failed - directory traversal not blocked!")
            except Exception as e:
                print(f"✓ Security test passed - exception raised: {e}")

            print("\n" + "=" * 80)
            print("All tests completed!")
            print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_server())
