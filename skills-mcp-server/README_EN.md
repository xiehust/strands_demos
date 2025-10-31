# Skills MCP Server

A Model Context Protocol (MCP) server that provides access to Strands skills through standardized tools and resources.

## Overview

This MCP server exposes skills from a directory structure, allowing AI agents to:
- Discover available skills with metadata
- Invoke skills to load their instructions
- Read skill files and supporting documentation
- List files within skill directories

## 🚀 Quick Start

- **Quick Start the MCP Sever**
Run below code, you will start a Http MCP sever in local
```bash
uv run src/server.py
```

**Quick Example:**
go to folder of file [agent_with_mcp.py](../strands_skills_demo/agent_with_mcp.py)
Run below code. 
```bash
python main.py --prompt "research about Claude Code Agent Skills (https://docs.claude.com/en/docs/claude-code/skills), and create a ppt in Chinese to introduce it, save it as pptx file in working directory."
```


## Features

### Tools

#### 1. **invoke_skill**
Load and activate a skill by name. Returns the full skill content with instructions, similar to the Strands Skill tool.

```python
invoke_skill(skill_name="pdf")
```

**Parameters:**
- `skill_name` (str): Name of the skill folder to invoke

**Returns:** Full skill content including metadata and instructions

---

#### 2. **read_skill_file**
Read any file from within a skill's directory. Provides access to supporting files like examples, documentation, and reference materials.

```python
read_skill_file(skill_name="pdf", file_path="reference.md")
```

**Parameters:**
- `skill_name` (str): Name of the skill folder
- `file_path` (str): Relative path to the file within the skill directory

**Returns:** Content of the requested file

**Security:** Prevents directory traversal attacks - only files within the skill directory can be accessed.

---

#### 3. **list_skill_files**
List all files and directories in a skill's folder or subfolder.

```python
list_skill_files(skill_name="pdf", subdirectory="examples")
```

**Parameters:**
- `skill_name` (str): Name of the skill folder
- `subdirectory` (str, optional): Subdirectory path within the skill (default: root)

**Returns:** Formatted list of files and directories with sizes

---

### Resources

#### 1. **skills://list**
Returns a formatted list of all available skills with their metadata.

**Includes:**
- Skill name
- Description
- Folder name
- License information (if available)

---

#### 2. **skills://{skill_name}**
Get the full content of a specific skill.

**Example:** `skills://pdf`

**Returns:** Complete skill including metadata, base directory, and full instructions

---



## Running the Server

### Standalone Mode (HTTP)

```bash
uv run src/server.py
```

The server will start in http mode and communicate via standard input/output.

---


**Important:** Use absolute paths for both the server script and the skills directory.

---

### With Other MCP Clients

The server uses streamable HTTP transport by default and is compatible with any MCP client that supports the Model Context Protocol.

Example using the MCP Python client:

```python
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("http://localhost:8000/mcp") as (read, write,_):
    async with ClientSession(read, write) as session:
        # Use the session
        await session.initialize()

        # Call tools
        result = await session.call_tool("invoke_skill", {"skill_name": "pdf"})
        print(result)
```

---

## Skill Directory Structure

Skills must follow this structure:

```
skills/
├── skill-name/
│   ├── SKILL.md          # Required: Main skill file with frontmatter
│   ├── reference.md      # Optional: Additional documentation
│   ├── examples/         # Optional: Example files
│   ├── forms.md          # Optional: Specific guides
│   └── ...               # Other supporting files
```

### SKILL.md Format

Each `SKILL.md` file must have YAML frontmatter:

```markdown
---
name: skill-name
description: Brief description of what the skill does
license: Optional license information
---

# Skill Content

Detailed instructions and documentation for the skill...

## Quick Start

Examples and usage instructions...
```

**Required fields:**
- `name`: Display name of the skill
- `description`: Brief description of the skill's purpose

**Optional fields:**
- `license`: License information

---

## Example Usage

### Using Resources

```python
# List all available skills
skills_list = await session.read_resource("skills://list")
print(skills_list[0].text)

# Get a specific skill's content
pdf_skill = await session.read_resource("skills://pdf")
print(pdf_skill[0].text)
```

### Using Tools

```python
# Invoke a skill
result = await session.call_tool("invoke_skill", {
    "skill_name": "pdf"
})

# Read a supporting file
reference = await session.call_tool("read_skill_file", {
    "skill_name": "pdf",
    "file_path": "reference.md"
})

# List files in a skill directory
files = await session.call_tool("list_skill_files", {
    "skill_name": "pdf",
    "subdirectory": ""
})

# Read a file from a subdirectory
example = await session.call_tool("read_skill_file", {
    "skill_name": "pdf",
    "file_path": "examples/create_invoice.py"
})
```

---

## Security

The server implements several security measures:

- **Directory Traversal Prevention**: File paths are resolved and validated to ensure they stay within the skills directory
- **Path Sanitization**: All file paths are checked against the base skills directory
- **Read-Only Access**: The server only provides read access to skill files
- **Scope Limitation**: Only files within configured skill directories are accessible

---

## Development

### Project Structure

```
skills-mcp-server/
├── src/
│   └── server.py         # Main MCP server implementation
├── tests/                # Test files (to be added)
├── .env.example          # Example environment configuration
├── .gitignore            # Git ignore patterns
├── pyproject.toml        # Project configuration and dependencies
└── README.md             # This file
```

## Troubleshooting

### Skills Not Found

**Problem:** Server reports "No skills found" or skill not found errors.

**Solutions:**
- Verify `SKILLS_DIR` environment variable points to the correct directory
- Ensure skill directories contain valid `SKILL.md` files
- Check that `SKILL.md` files have proper YAML frontmatter
- Verify file permissions allow reading

**Debug:**
```bash
export SKILLS_DIR=/path/to/skills
python src/server.py
# Check logs for directory being scanned
```

---

### Server Not Starting

**Problem:** Server fails to start or crashes immediately.

**Solutions:**
- Verify Python version is >= 3.10: `python --version`
- Ensure all dependencies are installed: `pip list | grep mcp`
- Check for syntax errors in `server.py`
- Review error messages in logs

---

### Invalid Skill Format

**Problem:** Skills are skipped during initialization.

**Solution:** Ensure `SKILL.md` has proper frontmatter:
```markdown
---
name: my-skill
description: My skill description
---

Content here...
```

---

### File Access Denied

**Problem:** Cannot read skill files.

**Solutions:**
- Ensure file paths are relative to the skill directory
- Check file permissions
- Verify the file exists: use `list_skill_files` first
- Don't use absolute paths or try to escape the skill directory

---

## Logging

The server logs key events to help with debugging:

- Skill scanning and initialization
- Tool invocations
- File read operations
- Errors and warnings

Logs use Python's standard logging module with INFO level by default.

To change log level:
```python
# In server.py
logging.basicConfig(level=logging.DEBUG)  # More verbose
```

---

## References

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Strands Agent Documentation](https://strands.dev)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk#fastmcp)

---

## Changelog

### v0.1.0 (2025-10-31)
- Initial release
- Basic skill invocation tools
- File reading capabilities
- Resource endpoints for skill discovery
- Security features (directory traversal prevention)
