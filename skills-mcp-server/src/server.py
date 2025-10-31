#!/usr/bin/env python3
"""
Skills MCP Server

This MCP server provides access to Strands skills through tools and resources.
It exposes skills from a configurable directory structure.
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("skills-mcp-server",stateless_http=True)

# Default skills directory (can be overridden via environment variable)
SKILLS_DIR = os.getenv("SKILLS_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "strands_skills_demo", "skills"))


def parse_skill_file(skill_path: str) -> Optional[Dict[str, Any]]:
    """
    Parse a SKILL.md file and extract metadata and content.

    Args:
        skill_path: Path to the SKILL.md file

    Returns:
        Dictionary with 'name', 'description', 'license', and 'content' keys, or None if parsing fails
    """
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse YAML frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)

        if not frontmatter_match:
            logger.warning(f"Invalid skill format (missing frontmatter): {skill_path}")
            return None

        yaml_content = frontmatter_match.group(1)
        markdown_content = frontmatter_match.group(2)

        # Parse name, description, and license from YAML
        name_match = re.search(r'name:\s*(.+)', yaml_content)
        desc_match = re.search(r'description:\s*(.+)', yaml_content)
        license_match = re.search(r'license:\s*(.+)', yaml_content)

        return {
            'name': name_match.group(1).strip() if name_match else None,
            'description': desc_match.group(1).strip() if desc_match else "No description available",
            'license': license_match.group(1).strip() if license_match else None,
            'content': markdown_content.strip()
        }
    except Exception as e:
        logger.error(f"Error parsing skill file {skill_path}: {e}")
        return None


def get_all_skills() -> List[Dict[str, Any]]:
    """
    Scan the skills directory and return metadata for all available skills.

    Returns:
        List of skill metadata dictionaries
    """
    skills = []
    skills_path = Path(SKILLS_DIR)

    if not skills_path.exists():
        logger.warning(f"Skills directory does not exist: {SKILLS_DIR}")
        return skills

    logger.info(f"Scanning skills directory: {SKILLS_DIR}")

    for skill_dir in skills_path.iterdir():
        if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        skill_data = parse_skill_file(str(skill_file))
        if skill_data:
            skill_data['folder'] = skill_dir.name
            skill_data['path'] = str(skill_dir)
            skills.append(skill_data)

    logger.info(f"Found {len(skills)} skills")
    return skills


def get_skill_by_name(skill_name: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific skill by name.

    Args:
        skill_name: Name of the skill

    Returns:
        Skill data dictionary or None if not found
    """
    skill_path = Path(SKILLS_DIR) / skill_name / "SKILL.md"

    if not skill_path.exists():
        logger.warning(f"Skill not found: {skill_name}")
        return None

    skill_data = parse_skill_file(str(skill_path))
    if skill_data:
        skill_data['folder'] = skill_name
        skill_data['path'] = str(skill_path.parent)

    return skill_data


# Resources

@mcp.resource("skills://list")
def list_skills() -> str:
    """
    Resource that lists all available skills with their metadata.

    Returns:
        Formatted list of skills with name, description, and folder
    """
    skills = get_all_skills()

    if not skills:
        return "No skills found."

    output = f"# Available Skills ({len(skills)})\n\n"

    for skill in sorted(skills, key=lambda s: s['name']):
        output += f"## {skill['name']}\n"
        output += f"**Folder**: `{skill['folder']}`\n\n"
        output += f"**Description**: {skill['description']}\n\n"
        if skill.get('license'):
            output += f"**License**: {skill['license']}\n\n"
        output += "---\n\n"

    return output


@mcp.resource("skills://{skill_name}")
def get_skill_content(skill_name: str) -> str:
    """
    Resource that returns the full content of a specific skill.

    Args:
        skill_name: Name of the skill folder

    Returns:
        Full skill content including metadata and instructions
    """
    skill_data = get_skill_by_name(skill_name)

    if not skill_data:
        return f"Error: Skill '{skill_name}' not found."

    output = f"# {skill_data['name']}\n\n"
    output += f"**Description**: {skill_data['description']}\n\n"

    if skill_data.get('license'):
        output += f"**License**: {skill_data['license']}\n\n"

    output += f"**Base Directory**: `{skill_data['path']}`\n\n"
    output += "---\n\n"
    output += skill_data['content']

    return output


# Tools

@mcp.tool()
def invoke_skill(skill_name: str) -> str:
    """
    Invoke a skill by name and return its full content.

    This tool is similar to the Strands Skill tool - it loads a skill's instructions
    and makes them available to the AI agent.

    Args:
        skill_name: Name of the skill to invoke (folder name)

    Returns:
        The full skill content with instructions and metadata
    """
    logger.info(f"Invoking skill: {skill_name}")

    skill_data = get_skill_by_name(skill_name)

    if not skill_data:
        return f"❌ Error: Skill '{skill_name}' not found.\n\nAvailable skills: {', '.join([s['folder'] for s in get_all_skills()])}"

    logger.info(f"✅ Skill '{skill_name}' invoked successfully")

    output = f"🎯 Skill '{skill_data['name']}' is now active\n\n"
    output += f"**Base Directory**: `{skill_data['path']}`\n\n"
    output += "---\n\n"
    output += skill_data['content']

    return output


@mcp.tool()
def read_skill_file(skill_name: str, file_path: str) -> str:
    """
    Read a file from within a skill's directory.

    This tool provides read access to any file within a skill's folder,
    allowing you to access supporting files like examples, documentation, etc.

    Args:
        skill_name: Name of the skill (folder name)
        file_path: Relative path to the file within the skill directory

    Returns:
        Content of the requested file
    """
    logger.info(f"Reading file '{file_path}' from skill '{skill_name}'")

    # Validate skill exists
    skill_dir = Path(SKILLS_DIR) / skill_name
    if not skill_dir.exists() or not skill_dir.is_dir():
        return f"❌ Error: Skill '{skill_name}' not found."

    # Resolve the file path (prevent directory traversal)
    try:
        full_path = (skill_dir / file_path).resolve()

        # Ensure the resolved path is within the skill directory
        if not str(full_path).startswith(str(skill_dir.resolve())):
            return f"❌ Error: Access denied. File must be within the skill directory."

        if not full_path.exists():
            return f"❌ Error: File '{file_path}' not found in skill '{skill_name}'."

        if not full_path.is_file():
            return f"❌ Error: '{file_path}' is not a file."

        # Read the file
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.info(f"✅ File '{file_path}' read successfully ({len(content)} chars)")

        return f"📄 File: {file_path}\n\n{content}"

    except Exception as e:
        logger.error(f"Error reading file '{file_path}' from skill '{skill_name}': {e}")
        return f"❌ Error reading file: {str(e)}"


@mcp.tool()
def list_skill_files(skill_name: str, subdirectory: str = "") -> str:
    """
    List all files in a skill's directory or subdirectory.

    Args:
        skill_name: Name of the skill (folder name)
        subdirectory: Optional subdirectory within the skill folder (default: root)

    Returns:
        List of files and directories
    """
    logger.info(f"Listing files in skill '{skill_name}', subdirectory: '{subdirectory}'")

    # Validate skill exists
    skill_dir = Path(SKILLS_DIR) / skill_name
    if not skill_dir.exists() or not skill_dir.is_dir():
        return f"❌ Error: Skill '{skill_name}' not found."

    try:
        # Resolve the target directory
        target_dir = (skill_dir / subdirectory).resolve()

        # Ensure the resolved path is within the skill directory
        if not str(target_dir).startswith(str(skill_dir.resolve())):
            return f"❌ Error: Access denied. Path must be within the skill directory."

        if not target_dir.exists():
            return f"❌ Error: Directory '{subdirectory}' not found in skill '{skill_name}'."

        if not target_dir.is_dir():
            return f"❌ Error: '{subdirectory}' is not a directory."

        # List contents
        files = []
        directories = []

        for item in sorted(target_dir.iterdir()):
            if item.is_file():
                size = item.stat().st_size
                files.append(f"  📄 {item.name} ({size} bytes)")
            elif item.is_dir():
                directories.append(f"  📁 {item.name}/")

        output = f"📂 Contents of '{skill_name}/{subdirectory}'\n\n"

        if directories:
            output += "**Directories:**\n" + "\n".join(directories) + "\n\n"

        if files:
            output += "**Files:**\n" + "\n".join(files) + "\n\n"

        if not directories and not files:
            output += "(empty directory)\n"

        logger.info(f"✅ Listed {len(files)} files and {len(directories)} directories")

        return output

    except Exception as e:
        logger.error(f"Error listing files in skill '{skill_name}': {e}")
        return f"❌ Error listing files: {str(e)}"


if __name__ == "__main__":
    # Run the server
    logger.info(f"Starting Skills MCP Server with skills directory: {SKILLS_DIR}")
    mcp.run(transport="streamable-http")
