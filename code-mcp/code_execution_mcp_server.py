#!/usr/bin/env python3
"""
Code Execution MCP Server - Following Anthropic's principles

This MCP server implements the code execution pattern described in:
https://www.anthropic.com/engineering/code-execution-with-mcp

Instead of loading all tool definitions upfront, this server:
1. Exposes tools as a virtual filesystem that agents can explore
2. Provides a code execution environment for agents to write Python code
3. Allows agents to discover and use tools progressively
4. Enables data filtering and transformation in the execution environment
5. Supports state persistence and skill building

Key benefits:
- Reduced token consumption through progressive tool discovery
- Context-efficient by processing data in execution environment
- More powerful control flow using native Python constructs
- Privacy-preserving operations (data stays in execution environment)
- Skill persistence and reusability
"""

import os
import sys
import json
import logging
import traceback
from pathlib import Path
from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import FastMCP
import inspect

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp_server = FastMCP("code-execution-mcp-server")

# Skills directory for persisting agent-created functions
SKILLS_DIR = os.getenv("SKILLS_DIR", os.path.join(os.path.dirname(__file__), "agent_skills"))
Path(SKILLS_DIR).mkdir(exist_ok=True)

# Execution environment state
EXECUTION_STATE = {
    'variables': {},
    'imports': set(),
    'skills': {}
}


def generate_tool_api_structure() -> Dict[str, Any]:
    """
    Generate a virtual filesystem structure representing available tools.

    This mimics the TypeScript approach from the article where tools are
    organized in a ./servers/ directory structure.

    Returns:
        Dictionary representing the tool API structure
    """
    # Example tools organized by "server" (category)
    tools = {
        "filesystem": {
            "description": "File and directory operations",
            "tools": {
                "read_file": {
                    "description": "Read content from a file",
                    "parameters": {
                        "path": "str - Path to the file",
                        "encoding": "str - File encoding (default: utf-8)"
                    },
                    "returns": "str - File content"
                },
                "write_file": {
                    "description": "Write content to a file",
                    "parameters": {
                        "path": "str - Path to the file",
                        "content": "str - Content to write",
                        "mode": "str - Write mode (default: 'w')"
                    },
                    "returns": "bool - Success status"
                },
                "list_directory": {
                    "description": "List contents of a directory",
                    "parameters": {
                        "path": "str - Directory path",
                        "recursive": "bool - Recursive listing (default: False)"
                    },
                    "returns": "List[str] - List of file paths"
                }
            }
        },
        "data_processing": {
            "description": "Data manipulation and analysis tools",
            "tools": {
                "filter_json": {
                    "description": "Filter JSON data by criteria",
                    "parameters": {
                        "data": "List[Dict] - JSON data to filter",
                        "filter_fn": "Callable - Filter function",
                    },
                    "returns": "List[Dict] - Filtered data"
                },
                "aggregate_data": {
                    "description": "Aggregate data with various operations",
                    "parameters": {
                        "data": "List[Dict] - Data to aggregate",
                        "group_by": "str - Field to group by",
                        "operation": "str - Aggregation operation (sum, avg, count, etc.)"
                    },
                    "returns": "Dict - Aggregated results"
                }
            }
        },
        "skills": {
            "description": "Manage and execute saved skills",
            "tools": {
                "list_skills": {
                    "description": "List all saved skills",
                    "parameters": {},
                    "returns": "List[str] - List of skill names"
                },
                "save_skill": {
                    "description": "Save a reusable skill function",
                    "parameters": {
                        "name": "str - Skill name",
                        "code": "str - Python code for the skill",
                        "description": "str - Skill description"
                    },
                    "returns": "bool - Success status"
                },
                "load_skill": {
                    "description": "Load and execute a saved skill",
                    "parameters": {
                        "name": "str - Skill name"
                    },
                    "returns": "Any - Skill function"
                }
            }
        }
    }

    return tools


@mcp_server.tool()
def search_tools(query: str, category: Optional[str] = None, detail_level: str = "summary") -> str:
    """
    Search for available tools by query string.

    This implements progressive disclosure - instead of loading all tool definitions
    upfront, the agent can search for relevant tools as needed.

    Args:
        query: Search query (searches in tool names and descriptions)
        category: Optional category filter (filesystem, data_processing, skills)
        detail_level: Level of detail - "name" (just names), "summary" (name + description),
                     or "full" (complete definition with schemas)

    Returns:
        Formatted string with matching tools at the requested detail level
    """
    logger.info(f"Tool search: query='{query}', category={category}, detail_level={detail_level}")

    tools_structure = generate_tool_api_structure()
    matches = []

    # Search through tools
    for cat_name, cat_data in tools_structure.items():
        # Filter by category if specified
        if category and cat_name != category:
            continue

        for tool_name, tool_data in cat_data.get('tools', {}).items():
            # Search in name and description
            if (query.lower() in tool_name.lower() or
                query.lower() in tool_data.get('description', '').lower()):
                matches.append({
                    'category': cat_name,
                    'name': tool_name,
                    'data': tool_data
                })

    if not matches:
        return f"No tools found matching '{query}'"

    # Format output based on detail level
    output = f"Found {len(matches)} tool(s) matching '{query}':\n\n"

    for match in matches:
        if detail_level == "name":
            output += f"- {match['category']}.{match['name']}\n"
        elif detail_level == "summary":
            output += f"## {match['category']}.{match['name']}\n"
            output += f"{match['data']['description']}\n\n"
        else:  # full
            output += f"## {match['category']}.{match['name']}\n"
            output += f"{match['data']['description']}\n\n"
            output += "**Parameters:**\n"
            for param, desc in match['data'].get('parameters', {}).items():
                output += f"  - `{param}`: {desc}\n"
            output += f"\n**Returns:** {match['data'].get('returns', 'None')}\n\n"
            output += "---\n\n"

    logger.info(f"Found {len(matches)} matching tools")
    return output


@mcp_server.tool()
def list_tool_categories() -> str:
    """
    List all available tool categories.

    This helps agents discover what kinds of tools are available without
    loading all definitions into context.

    Returns:
        Formatted list of categories with descriptions
    """
    logger.info("Listing tool categories")

    tools_structure = generate_tool_api_structure()

    output = "Available Tool Categories:\n\n"
    for category, data in tools_structure.items():
        tool_count = len(data.get('tools', {}))
        output += f"## {category}\n"
        output += f"{data['description']}\n"
        output += f"Tools: {tool_count}\n\n"

    return output


@mcp_server.tool()
def execute_code(
    code: str,
    return_value: bool = True,
    persist_state: bool = True
) -> str:
    """
    Execute Python code in a persistent execution environment.

    This is the core of the code execution pattern. Instead of making direct
    tool calls, agents write Python code that interacts with MCP tools through
    a code API.

    Benefits:
    - Data can be filtered/transformed before returning to the model
    - Complex control flow using native Python constructs
    - State persistence across executions
    - Intermediate results don't flow through model context

    Args:
        code: Python code to execute
        return_value: Whether to return the last expression's value
        persist_state: Whether to persist variables in execution state

    Returns:
        Execution result or output

    Example:
        ```python
        # Agent writes code like this:
        from tools.filesystem import read_file, list_directory
        from tools.data_processing import filter_json

        # Read large dataset
        data = read_file('/data/large_dataset.json')

        # Filter in execution environment (not in model context!)
        filtered = [item for item in data if item['status'] == 'active']

        # Only return summary to model
        print(f"Found {len(filtered)} active items")
        print(f"First 5: {filtered[:5]}")
        ```
    """
    logger.info("Executing code in persistent environment")
    logger.debug(f"Code:\n{code}")

    try:
        # Prepare execution environment
        exec_globals = {
            '__builtins__': __builtins__,
            'json': json,
            'os': os,
            'Path': Path,
            # Add tool API modules
            'tools': ToolsAPI(),
        }

        # Add persisted state
        if persist_state:
            exec_globals.update(EXECUTION_STATE['variables'])

        exec_locals = {}

        # Capture stdout
        from io import StringIO
        import contextlib

        stdout_capture = StringIO()

        with contextlib.redirect_stdout(stdout_capture):
            # Execute the code
            exec(code, exec_globals, exec_locals)

        # Get captured output
        output = stdout_capture.getvalue()

        # Persist state if requested
        if persist_state:
            # Update persisted variables (excluding builtins and imports)
            for key, value in exec_locals.items():
                if not key.startswith('_') and not callable(value):
                    EXECUTION_STATE['variables'][key] = value

        # Return result
        result = {
            'output': output,
            'success': True
        }

        if return_value and exec_locals:
            # Get the last expression's value if any
            last_key = list(exec_locals.keys())[-1] if exec_locals else None
            if last_key:
                result['return_value'] = str(exec_locals[last_key])

        formatted_output = "✅ Code executed successfully\n\n"
        if output:
            formatted_output += f"Output:\n{output}\n\n"
        if 'return_value' in result:
            formatted_output += f"Return value: {result['return_value']}\n"

        logger.info("Code execution completed successfully")
        return formatted_output

    except Exception as e:
        error_msg = f"❌ Error executing code:\n{str(e)}\n\n"
        error_msg += f"Traceback:\n{traceback.format_exc()}"
        logger.error(f"Code execution failed: {e}")
        return error_msg


class ToolsAPI:
    """
    Tools API that agents can import and use in their code.

    This provides a code-friendly interface to MCP tools, implementing
    the pattern from the article where tools are accessed as Python functions
    rather than through direct MCP tool calls.
    """

    class FilesystemTools:
        """Filesystem operations tools"""

        @staticmethod
        def read_file(path: str, encoding: str = 'utf-8') -> str:
            """Read content from a file"""
            with open(path, 'r', encoding=encoding) as f:
                return f.read()

        @staticmethod
        def write_file(path: str, content: str, mode: str = 'w') -> bool:
            """Write content to a file"""
            with open(path, mode) as f:
                f.write(content)
            return True

        @staticmethod
        def list_directory(path: str, recursive: bool = False) -> List[str]:
            """List contents of a directory"""
            if recursive:
                files = []
                for root, _, filenames in os.walk(path):
                    for filename in filenames:
                        files.append(os.path.join(root, filename))
                return files
            else:
                return [os.path.join(path, f) for f in os.listdir(path)]

    class DataProcessingTools:
        """Data processing and analysis tools"""

        @staticmethod
        def filter_json(data: List[Dict], filter_fn) -> List[Dict]:
            """Filter JSON data by criteria"""
            return [item for item in data if filter_fn(item)]

        @staticmethod
        def aggregate_data(data: List[Dict], group_by: str, operation: str) -> Dict:
            """Aggregate data with various operations"""
            from collections import defaultdict

            groups = defaultdict(list)
            for item in data:
                key = item.get(group_by)
                groups[key].append(item)

            result = {}
            for key, items in groups.items():
                if operation == 'count':
                    result[key] = len(items)
                elif operation == 'sum':
                    result[key] = sum(item.get('value', 0) for item in items)
                elif operation == 'avg':
                    values = [item.get('value', 0) for item in items]
                    result[key] = sum(values) / len(values) if values else 0

            return result

    class SkillsTools:
        """Skill management tools"""

        @staticmethod
        def list_skills() -> List[str]:
            """List all saved skills"""
            skills_path = Path(SKILLS_DIR)
            return [f.stem for f in skills_path.glob("*.py")]

        @staticmethod
        def save_skill(name: str, code: str, description: str = "") -> bool:
            """Save a reusable skill function"""
            skill_path = Path(SKILLS_DIR) / f"{name}.py"

            # Create skill file with metadata
            skill_content = f'''"""
{description}

Skill: {name}
Auto-generated skill function
"""

{code}
'''

            with open(skill_path, 'w') as f:
                f.write(skill_content)

            # Store in execution state
            EXECUTION_STATE['skills'][name] = code

            logger.info(f"Skill '{name}' saved to {skill_path}")
            return True

        @staticmethod
        def load_skill(name: str):
            """Load and execute a saved skill"""
            skill_path = Path(SKILLS_DIR) / f"{name}.py"

            if not skill_path.exists():
                raise FileNotFoundError(f"Skill '{name}' not found")

            # Load the skill code
            with open(skill_path, 'r') as f:
                code = f.read()

            # Execute in a namespace
            namespace = {}
            exec(code, namespace)

            # Return the main function (convention: same name as skill)
            if name in namespace:
                return namespace[name]

            # Return the namespace if no matching function
            return namespace

    def __init__(self):
        self.filesystem = self.FilesystemTools()
        self.data_processing = self.DataProcessingTools()
        self.skills = self.SkillsTools()


@mcp_server.tool()
def save_skill(name: str, code: str, description: str = "") -> str:
    """
    Save a reusable skill function for future use.

    This implements the skill persistence pattern from the article. Agents can
    develop working code and save it as a skill that can be reused later.

    Args:
        name: Name of the skill
        code: Python code implementing the skill
        description: Description of what the skill does

    Returns:
        Success message with skill location

    Example:
        An agent might create a skill like:

        ```python
        def export_filtered_data(file_path, filter_key, filter_value, output_format='json'):
            '''Export filtered data to various formats'''
            from tools.filesystem import read_file, write_file
            import json

            # Read data
            data = json.loads(read_file(file_path))

            # Filter
            filtered = [item for item in data if item.get(filter_key) == filter_value]

            # Export
            if output_format == 'json':
                output = json.dumps(filtered, indent=2)
            elif output_format == 'csv':
                # Convert to CSV
                import csv
                from io import StringIO
                output_buffer = StringIO()
                if filtered:
                    writer = csv.DictWriter(output_buffer, fieldnames=filtered[0].keys())
                    writer.writeheader()
                    writer.writerows(filtered)
                output = output_buffer.getvalue()

            write_file(f'output.{output_format}', output)
            return len(filtered)
        ```
    """
    logger.info(f"Saving skill: {name}")

    try:
        tools_api = ToolsAPI()
        success = tools_api.skills.save_skill(name, code, description)

        if success:
            output = f"✅ Skill '{name}' saved successfully\n\n"
            output += f"Location: {SKILLS_DIR}/{name}.py\n"
            output += f"Description: {description}\n\n"
            output += "You can now use this skill in future executions by importing it:\n"
            output += f"```python\nfrom tools.skills import load_skill\n{name} = load_skill('{name}')\n```"

            return output
        else:
            return f"❌ Failed to save skill '{name}'"

    except Exception as e:
        return f"❌ Error saving skill: {str(e)}"


@mcp_server.tool()
def list_saved_skills() -> str:
    """
    List all saved skills in the skills directory.

    Returns:
        Formatted list of saved skills with their descriptions
    """
    logger.info("Listing saved skills")

    try:
        skills_path = Path(SKILLS_DIR)
        skill_files = list(skills_path.glob("*.py"))

        if not skill_files:
            return "No saved skills found."

        output = f"📚 Saved Skills ({len(skill_files)}):\n\n"

        for skill_file in sorted(skill_files):
            name = skill_file.stem

            # Try to extract description from docstring
            with open(skill_file, 'r') as f:
                lines = f.readlines()
                description = "No description"
                if len(lines) > 1 and lines[1].strip():
                    description = lines[1].strip()

            output += f"## {name}\n"
            output += f"{description}\n"
            output += f"File: {skill_file}\n\n"

        return output

    except Exception as e:
        return f"❌ Error listing skills: {str(e)}"


@mcp_server.tool()
def get_execution_state() -> str:
    """
    Get the current execution state (persisted variables and skills).

    This allows agents to see what state has been persisted across
    code executions, enabling them to build on previous work.

    Returns:
        JSON representation of the execution state
    """
    logger.info("Getting execution state")

    state_summary = {
        'variables': {k: type(v).__name__ for k, v in EXECUTION_STATE['variables'].items()},
        'skills': list(EXECUTION_STATE['skills'].keys()),
        'imports': list(EXECUTION_STATE['imports'])
    }

    output = "📊 Current Execution State:\n\n"
    output += "**Persisted Variables:**\n"
    for var, var_type in state_summary['variables'].items():
        output += f"  - {var}: {var_type}\n"

    output += "\n**Loaded Skills:**\n"
    for skill in state_summary['skills']:
        output += f"  - {skill}\n"

    return output


@mcp_server.tool()
def reset_execution_state() -> str:
    """
    Reset the execution state (clear all persisted variables and skills).

    Returns:
        Confirmation message
    """
    logger.info("Resetting execution state")

    EXECUTION_STATE['variables'].clear()
    EXECUTION_STATE['skills'].clear()
    EXECUTION_STATE['imports'].clear()

    return "✅ Execution state reset successfully"


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Code Execution MCP Server")
    logger.info("Following Anthropic's code execution pattern")
    logger.info("=" * 60)
    logger.info(f"Skills Directory: {SKILLS_DIR}")
    logger.info("=" * 60)

    # Run the server
    logger.info("Starting MCP server...")
    mcp_server.run()
