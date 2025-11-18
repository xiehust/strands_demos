#!/usr/bin/env python3
"""
Skills MCP Server (AgentCore Compatible Version)

This MCP server provides access to Strands skills through tools only.
Resources have been removed for compatibility with clients that don't support MCP resources.
It exposes skills from a configurable directory structure.
"""

import os
import re
import logging
import subprocess
import glob
import shutil
import mimetypes
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from mcp.server.fastmcp import FastMCP
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp_server = FastMCP("skills-mcp-server",stateless_http=True)

# Default skills directory (can be overridden via environment variable)
SKILLS_DIR = os.getenv("SKILLS_DIR", os.path.join(os.path.dirname(__file__), "skills"))


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


# Tools (Resources functionality converted to tools for AgentCore compatibility)

@mcp_server.tool()
def list_all_skills() -> str:
    """
    List all available skills with their metadata.

    This tool replaces the 'skills://list' resource and provides the same functionality
    through the tool interface for clients that don't support MCP resources.

    Returns:
        Formatted list of skills with name, description, and folder
    """
    logger.info("Listing all skills via tool")

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

    logger.info(f"✅ Listed {len(skills)} skills")
    return output


@mcp_server.tool()
def invoke_skill(skill_name: str) -> str:
    """
    Invoke a skill by name and return its full content.

    This tool is similar to the Strands Skill tool - it loads a skill's instructions
    and makes them available to the AI agent. It also replaces the 'skills://{skill_name}'
    resource functionality for clients that don't support MCP resources.

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


@mcp_server.tool()
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


@mcp_server.tool()
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


# @mcp_server.tool()
def file_read(
    path: str,
    mode: str = "view",
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    search_pattern: Optional[str] = None,
    context_lines: int = 2,
    recursive: bool = True
) -> str:
    """
    Read file contents with various modes.

    This tool provides comprehensive file reading capabilities with multiple modes:
    - view: Display full file contents
    - find: List matching files (supports wildcards like *.py)
    - lines: Show specific line ranges
    - search: Pattern searching with context
    - stats: File statistics

    Args:
        path: Path to file(s). Supports wildcards (e.g., "*.py", "src/**/*.js")
        mode: Reading mode - "view", "find", "lines", "search", or "stats"
        start_line: Starting line number for "lines" mode (1-based)
        end_line: Ending line number for "lines" mode
        search_pattern: Pattern to search for in "search" mode
        context_lines: Number of context lines around search results (default: 2)
        recursive: Search recursively in subdirectories for "find" mode (default: True)

    Returns:
        File contents or search results based on the mode
    """
    logger.info(f"Reading file(s): {path}, mode: {mode}")

    try:
        # Expand user path
        path = os.path.expanduser(path)

        # MODE: find - List matching files
        if mode == "find":
            matching_files = []

            if os.path.exists(path):
                if os.path.isfile(path):
                    matching_files = [path]
                elif os.path.isdir(path):
                    for root, _, files in os.walk(path):
                        if not recursive and root != path:
                            continue
                        for file in sorted(files):
                            if not file.startswith("."):
                                matching_files.append(os.path.join(root, file))
            else:
                # Handle glob patterns
                if recursive and "**" not in path:
                    base_dir = os.path.dirname(path)
                    file_pattern = os.path.basename(path)
                    path = os.path.join(base_dir if base_dir else ".", "**", file_pattern)
                matching_files = glob.glob(path, recursive=recursive)

            matching_files = sorted(matching_files)

            if not matching_files:
                return f"❌ No files found matching pattern: {path}"

            output = f"📁 Found {len(matching_files)} file(s) matching '{path}':\n\n"
            for file in matching_files:
                file_size = os.path.getsize(file)
                output += f"  📄 {file} ({file_size} bytes)\n"

            logger.info(f"✅ Found {len(matching_files)} files")
            return output

        # For other modes, ensure the file exists
        if not os.path.exists(path):
            return f"❌ Error: File not found: {path}"

        if not os.path.isfile(path):
            return f"❌ Error: Path is not a file: {path}"

        # MODE: stats - File statistics
        if mode == "stats":
            file_size = os.path.getsize(path)
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                line_count = len(lines)
                preview = "".join(lines[:10])  # First 10 lines

            output = f"📊 File Statistics for {os.path.basename(path)}\n\n"
            output += f"File Path: {path}\n"
            output += f"File Size: {file_size} bytes ({file_size / 1024:.2f} KB)\n"
            output += f"Line Count: {line_count}\n\n"
            output += f"Preview (first 10 lines):\n{'-' * 50}\n{preview}"

            logger.info(f"✅ Stats retrieved for {path}")
            return output

        # MODE: view - Display full file contents
        if mode == "view":
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            output = f"📄 File: {path}\n\n{content}"
            logger.info(f"✅ File viewed: {path} ({len(content)} chars)")
            return output

        # MODE: lines - Show specific line ranges
        if mode == "lines":
            if start_line is None:
                return "❌ Error: start_line is required for 'lines' mode"

            with open(path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()

            # Convert to 0-based indexing
            start_idx = max(start_line - 1, 0)
            end_idx = min(end_line, len(all_lines)) if end_line else len(all_lines)

            if start_idx >= len(all_lines):
                return f"❌ Error: start_line ({start_line}) exceeds file length ({len(all_lines)} lines)"

            selected_lines = all_lines[start_idx:end_idx]

            output = f"📄 Lines {start_line}-{end_idx} from {os.path.basename(path)}\n\n"
            for i, line in enumerate(selected_lines, start=start_line):
                output += f"{i:4d} | {line}"

            logger.info(f"✅ Lines {start_line}-{end_idx} read from {path}")
            return output

        # MODE: search - Pattern searching with context
        if mode == "search":
            if not search_pattern:
                return "❌ Error: search_pattern is required for 'search' mode"

            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            matches = []
            for i, line in enumerate(lines):
                if search_pattern.lower() in line.lower():
                    # Get context lines
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 1)

                    context = []
                    for ctx_idx in range(start, end):
                        prefix = "→ " if ctx_idx == i else "  "
                        context.append(f"{prefix}{ctx_idx + 1:4d} | {lines[ctx_idx].rstrip()}")

                    matches.append({
                        'line_number': i + 1,
                        'context': "\n".join(context)
                    })

            if not matches:
                return f"❌ No matches found for pattern '{search_pattern}' in {os.path.basename(path)}"

            output = f"🔍 Found {len(matches)} match(es) for '{search_pattern}' in {os.path.basename(path)}\n\n"
            for match in matches:
                output += f"Match at line {match['line_number']}:\n{match['context']}\n\n"

            logger.info(f"✅ Found {len(matches)} matches for '{search_pattern}'")
            return output

        return f"❌ Error: Invalid mode '{mode}'. Supported modes: view, find, lines, search, stats"

    except Exception as e:
        logger.error(f"Error in file_read: {e}")
        return f"❌ Error reading file: {str(e)}"


# @mcp_server.tool()
def file_write(path: str, content: str, create_directories: bool = True) -> str:
    """
    Write content to a file.

    This tool safely writes the provided content to a specified file path.
    It can automatically create parent directories if they don't exist.

    Args:
        path: Path to the file to write. Supports user path expansion (e.g., ~/)
        content: The content to write to the file
        create_directories: Whether to create parent directories if they don't exist (default: True)

    Returns:
        Success or error message with file information
    """
    logger.info(f"Writing to file: {path}")

    try:
        # Expand user path
        path = os.path.expanduser(path)

        # Create parent directories if requested
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            if create_directories:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            else:
                return f"❌ Error: Directory does not exist: {directory}"

        # Write the file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Get file info
        file_size = os.path.getsize(path)
        char_count = len(content)
        line_count = content.count('\n') + 1

        output = f"✅ File written successfully\n\n"
        output += f"Path: {path}\n"
        output += f"Size: {file_size} bytes ({file_size / 1024:.2f} KB)\n"
        output += f"Characters: {char_count}\n"
        output += f"Lines: {line_count}\n"

        logger.info(f"✅ File written: {path} ({char_count} chars, {line_count} lines)")
        return output

    except PermissionError as e:
        logger.error(f"Permission denied writing to {path}: {e}")
        return f"❌ Error: Permission denied writing to {path}"
    except Exception as e:
        logger.error(f"Error writing file: {e}")
        return f"❌ Error writing file: {str(e)}"


# @mcp_server.tool()
def editor(
    command: str,
    path: str,
    file_text: Optional[str] = None,
    old_str: Optional[str] = None,
    new_str: Optional[str] = None,
    insert_line: Optional[Union[str, int]] = None,
    view_range: Optional[List[int]] = None
) -> str:
    """
    Editor tool for iterative file modifications.

    This tool provides comprehensive file editing capabilities including viewing,
    creating, replacing text, and inserting content at specific locations.

    Commands:
    - view: Display file contents or directory structure
    - create: Create a new file with specified content
    - str_replace: Replace exact string matches in a file
    - insert: Insert text after a specified line
    - undo_edit: Restore file from backup

    Args:
        command: Command to execute - "view", "create", "str_replace", "insert", or "undo_edit"
        path: Absolute or relative path to file/directory. Supports ~ expansion
        file_text: Content for new file (required for "create" command)
        old_str: Text to find and replace (required for "str_replace" command)
        new_str: Replacement text (required for "str_replace" and "insert" commands)
        insert_line: Line number (int) or search text (str) for insertion point (required for "insert")
        view_range: Optional [start, end] line numbers for viewing specific ranges

    Returns:
        Status message with operation details
    """
    logger.info(f"Editor command: {command} on {path}")

    try:
        # Expand user path
        path = os.path.expanduser(path)

        # Validate command
        valid_commands = ["view", "create", "str_replace", "insert", "undo_edit"]
        if command not in valid_commands:
            return f"❌ Error: Invalid command '{command}'. Valid commands: {', '.join(valid_commands)}"

        # VIEW command
        if command == "view":
            if os.path.isfile(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if view_range:
                    lines = content.split('\n')
                    start = max(0, view_range[0] - 1) if len(view_range) > 0 else 0
                    end = min(len(lines), view_range[1]) if len(view_range) > 1 else len(lines)
                    content = '\n'.join(lines[start:end])
                    range_info = f" (lines {view_range[0]}-{view_range[1]})"
                else:
                    range_info = ""

                output = f"📄 File: {os.path.basename(path)}{range_info}\n\n{content}"
                logger.info(f"✅ File viewed: {path}")
                return output

            elif os.path.isdir(path):
                # List directory contents
                items = []
                for item in sorted(os.listdir(path)):
                    if item.startswith('.'):
                        continue
                    full_path = os.path.join(path, item)
                    if os.path.isdir(full_path):
                        items.append(f"  📁 {item}/")
                    else:
                        size = os.path.getsize(full_path)
                        items.append(f"  📄 {item} ({size} bytes)")

                output = f"📁 Directory: {path}\n\n"
                output += '\n'.join(items) if items else "(empty directory)"
                logger.info(f"✅ Directory viewed: {path}")
                return output

            else:
                return f"❌ Error: Path does not exist: {path}"

        # CREATE command
        if command == "create":
            if not file_text:
                return "❌ Error: file_text is required for 'create' command"

            # Create parent directories if needed
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)

            # Write the file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(file_text)

            file_size = os.path.getsize(path)
            line_count = file_text.count('\n') + 1

            output = f"✅ File created successfully\n\n"
            output += f"Path: {path}\n"
            output += f"Size: {file_size} bytes\n"
            output += f"Lines: {line_count}\n"

            logger.info(f"✅ File created: {path}")
            return output

        # STR_REPLACE command
        if command == "str_replace":
            if not old_str or new_str is None:
                return "❌ Error: Both old_str and new_str are required for 'str_replace' command"

            if not os.path.exists(path):
                return f"❌ Error: File not found: {path}"

            # Read current content
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Count occurrences
            count = content.count(old_str)
            if count == 0:
                return f"❌ Error: old_str not found in {path}\n\nSearched for: {old_str}"

            # Create backup
            backup_path = f"{path}.bak"
            shutil.copy2(path, backup_path)

            # Make replacement
            new_content = content.replace(old_str, new_str)

            # Write new content
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            output = f"✅ Text replacement complete\n\n"
            output += f"File: {path}\n"
            output += f"Replacements: {count}\n"
            output += f"Old text: {old_str[:50]}{'...' if len(old_str) > 50 else ''}\n"
            output += f"New text: {new_str[:50]}{'...' if len(new_str) > 50 else ''}\n"
            output += f"Backup: {backup_path}\n"

            logger.info(f"✅ Replaced {count} occurrence(s) in {path}")
            return output

        # INSERT command
        if command == "insert":
            if not new_str or insert_line is None:
                return "❌ Error: Both new_str and insert_line are required for 'insert' command"

            if not os.path.exists(path):
                return f"❌ Error: File not found: {path}"

            # Read current content
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            # Handle string-based line finding
            if isinstance(insert_line, str):
                found = False
                for i, line in enumerate(lines):
                    if insert_line in line:
                        insert_line = i + 1  # Insert after this line
                        found = True
                        break
                if not found:
                    return f"❌ Error: Could not find '{insert_line}' in {path}"

            # Validate line number
            insert_line = int(insert_line)
            if insert_line < 0 or insert_line > len(lines):
                return f"❌ Error: insert_line {insert_line} is out of range (0-{len(lines)})"

            # Create backup
            backup_path = f"{path}.bak"
            shutil.copy2(path, backup_path)

            # Insert the new line
            lines.insert(insert_line, new_str)
            new_content = '\n'.join(lines)

            # Write new content
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # Show context
            context_start = max(0, insert_line - 2)
            context_end = min(len(lines), insert_line + 3)
            context = []
            for i in range(context_start, context_end):
                prefix = "→ " if i == insert_line else "  "
                context.append(f"{prefix}{i + 1:4d} | {lines[i]}")

            output = f"✅ Text insertion complete\n\n"
            output += f"File: {path}\n"
            output += f"Inserted at line: {insert_line + 1}\n"
            output += f"Backup: {backup_path}\n\n"
            output += "Context:\n" + '\n'.join(context)

            logger.info(f"✅ Inserted text at line {insert_line + 1} in {path}")
            return output

        # UNDO_EDIT command
        if command == "undo_edit":
            backup_path = f"{path}.bak"

            if not os.path.exists(backup_path):
                return f"❌ Error: No backup file found for {path}"

            # Restore from backup
            shutil.copy2(backup_path, path)
            os.remove(backup_path)

            output = f"✅ File restored from backup\n\n"
            output += f"File: {path}\n"
            output += f"Backup removed: {backup_path}\n"

            logger.info(f"✅ Restored {path} from backup")
            return output

        return f"❌ Error: Command '{command}' not fully implemented"

    except Exception as e:
        logger.error(f"Error in editor: {e}")
        return f"❌ Error: {str(e)}"


# @mcp_server.tool()
def s3_upload(
    file_path: str,
    bucket_name: Optional[str] = None,
    object_key: Optional[str] = None,
    expiration: int = 604800
) -> str:
    """
    Upload a file to S3 and return a presigned URL for download.

    This tool uploads a local file to an S3 bucket and generates a presigned URL
    that can be used to download the file. If no bucket is specified, it creates
    or uses a default bucket in the current AWS region.

    Features:
    - Automatic bucket creation with default naming
    - Content type detection based on file extension
    - Presigned URL generation with configurable expiration
    - Maximum expiration time: 7 days (604800 seconds)

    Args:
        file_path: Path to the local file to upload
        bucket_name: S3 bucket name (optional). If not provided, uses/creates default bucket
                    named 'skills-mcp-server-{region}-{account_id}'
        object_key: S3 object key (optional). If not provided, uses the filename
        expiration: Presigned URL expiration in seconds (default: 604800 = 7 days, max: 604800)

    Returns:
        JSON string with upload details and presigned URL

    Examples:
        1. Upload with default bucket:
           s3_upload(file_path="/tmp/data.json")

        2. Upload to specific bucket:
           s3_upload(file_path="/tmp/report.pdf", bucket_name="my-bucket")

        3. Custom object key and expiration:
           s3_upload(
               file_path="/tmp/file.txt",
               object_key="reports/2024/file.txt",
               expiration=3600
           )
    """
    logger.info(f"S3 upload request: {file_path}")

    try:
        # Expand user path
        file_path = os.path.expanduser(file_path)

        # Check if file exists
        if not os.path.exists(file_path):
            return f"❌ Error: File not found: {file_path}"

        if not os.path.isfile(file_path):
            return f"❌ Error: Path is not a file: {file_path}"

        # Validate expiration (max 7 days)
        if expiration > 604800:
            logger.warning(f"Expiration {expiration}s exceeds max 604800s, using max")
            expiration = 604800

        # Get file info
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)

        # Detect content type
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'

        # Initialize S3 client
        s3_client = boto3.client('s3')

        # Get current region and account ID
        sts_client = boto3.client('sts')
        account_id = sts_client.get_caller_identity()['Account']
        region = s3_client.meta.region_name or 'us-east-1'

        # Use default bucket name if not provided
        if not bucket_name:
            bucket_name = f"skills-mcp-server-{region}-{account_id}"
            logger.info(f"Using default bucket: {bucket_name}")

        # Check if bucket exists, create if it doesn't
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            logger.info(f"Bucket {bucket_name} exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                logger.info(f"Creating bucket: {bucket_name}")
                try:
                    if region == 'us-east-1':
                        s3_client.create_bucket(Bucket=bucket_name)
                    else:
                        s3_client.create_bucket(
                            Bucket=bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': region}
                        )
                    logger.info(f"✅ Bucket created: {bucket_name}")
                except ClientError as create_error:
                    return f"❌ Error creating bucket: {str(create_error)}"
            else:
                return f"❌ Error checking bucket: {str(e)}"

        # Use filename as object key if not provided
        if not object_key:
            object_key = file_name

        # Upload the file
        logger.info(f"Uploading {file_path} to s3://{bucket_name}/{object_key}")

        extra_args = {'ContentType': content_type}
        s3_client.upload_file(
            file_path,
            bucket_name,
            object_key,
            ExtraArgs=extra_args
        )

        logger.info(f"✅ File uploaded successfully")

        # Generate presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_key
            },
            ExpiresIn=expiration
        )

        # Calculate expiration time
        from datetime import datetime, timedelta, timezone
        expiration_time = datetime.now(timezone.utc) + timedelta(seconds=expiration)

        # Format output
        output = f"✅ File uploaded to S3 successfully\n\n"
        output += f"📁 Local File: {file_path}\n"
        output += f"📦 S3 Bucket: {bucket_name}\n"
        output += f"🔑 Object Key: {object_key}\n"
        output += f"📊 File Size: {file_size} bytes ({file_size / 1024:.2f} KB)\n"
        output += f"📄 Content Type: {content_type}\n"
        output += f"🌍 Region: {region}\n"
        output += f"⏱️ URL Expires: {expiration_time.strftime('%Y-%m-%d %H:%M:%S')} UTC ({expiration}s)\n\n"
        output += f"🔗 Presigned URL:\n{presigned_url}\n"

        logger.info(f"✅ Presigned URL generated, expires in {expiration}s")
        return output

    except ClientError as e:
        error_msg = f"AWS S3 error: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Error uploading to S3: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"


# @mcp_server.tool()
def shell(
    command: Union[str, List[str]],
    working_directory: Optional[str] = None,
    timeout: Optional[int] = None,
    ignore_errors: bool = False
) -> str:
    """
    Execute shell command(s) with support for multiple commands and error handling.

    SECURITY WARNING: This tool executes arbitrary shell commands. Use with caution
    and only with trusted input. Commands are executed with the same permissions
    as the MCP server process.

    Features:
    - Single or multiple command execution
    - Sequential command execution with directory context
    - Configurable timeout per command
    - Optional error handling (continue on failures)
    - Automatic working directory creation

    Args:
        command: Single command string or list of commands to execute sequentially.
                 For multiple commands, use array format: ["cmd1", "cmd2", "cmd3"]
        working_directory: Working directory for command execution (default: /app/workspace)
        timeout: Timeout in seconds for each command (default: 300). Set to None for no timeout.
        ignore_errors: If True, continue executing remaining commands even if one fails (default: False)

    Returns:
        Formatted output with results for all executed commands

    Examples:
        1. Single command:
           shell(command="ls -la")

        2. Multiple commands:
           shell(command=["mkdir test", "cd test", "touch file.txt"])

        3. With timeout and error handling:
           shell(command=["long-task"], timeout=600, ignore_errors=True)

        4. Custom working directory:
           shell(command="npm install", working_directory="/app/project")
    """
    # Default timeout from environment or 300 seconds
    if timeout is None:
        timeout = int(os.getenv("SHELL_DEFAULT_TIMEOUT", "300"))

    # Default working directory
    if working_directory is None:
        working_directory = "/app/workspace"

    # Normalize command to list
    commands = [command] if isinstance(command, str) else command

    logger.info(f"Executing {len(commands)} command(s), timeout={timeout}s, ignore_errors={ignore_errors}")

    # Create working directory if it doesn't exist
    working_dir_path = Path(working_directory)
    if not working_dir_path.exists():
        try:
            working_dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created working directory: {working_directory}")
        except Exception as e:
            logger.error(f"Failed to create working directory: {e}")
            return f"❌ Error: Failed to create working directory '{working_directory}': {str(e)}"

    # Track execution context
    current_dir = working_directory
    results = []
    success_count = 0
    failed_count = 0

    # Execute commands sequentially
    for idx, cmd in enumerate(commands, 1):
        logger.info(f"Executing command {idx}/{len(commands)}: {cmd}")

        try:
            # Execute the command
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=current_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # Track success/failure
            if result.returncode == 0:
                success_count += 1
                status = "✅ Success"
            else:
                failed_count += 1
                status = f"❌ Failed (exit code: {result.returncode})"

            # Store result
            result_entry = {
                'command': cmd,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'status': status,
                'working_dir': current_dir
            }
            results.append(result_entry)

            logger.info(f"Command {idx} completed with exit code {result.returncode}")

            # Update working directory if command was 'cd'
            if cmd.strip().startswith('cd ') and result.returncode == 0:
                new_dir = cmd.split('cd ', 1)[1].strip()
                if new_dir.startswith('/'):
                    current_dir = os.path.abspath(new_dir)
                else:
                    current_dir = os.path.abspath(os.path.join(current_dir, new_dir))
                logger.info(f"Updated working directory to: {current_dir}")

            # Stop on error if ignore_errors is False
            if result.returncode != 0 and not ignore_errors:
                logger.warning(f"Stopping execution due to error in command {idx}")
                break

        except subprocess.TimeoutExpired:
            failed_count += 1
            error_msg = f"Command timed out after {timeout} seconds"
            logger.error(f"Command {idx} timed out")

            result_entry = {
                'command': cmd,
                'exit_code': -1,
                'stdout': '',
                'stderr': error_msg,
                'status': '⏱️ Timeout',
                'working_dir': current_dir
            }
            results.append(result_entry)

            if not ignore_errors:
                logger.warning(f"Stopping execution due to timeout in command {idx}")
                break

        except Exception as e:
            failed_count += 1
            logger.error(f"Error executing command {idx}: {e}")

            result_entry = {
                'command': cmd,
                'exit_code': -1,
                'stdout': '',
                'stderr': str(e),
                'status': '❌ Error',
                'working_dir': current_dir
            }
            results.append(result_entry)

            if not ignore_errors:
                logger.warning(f"Stopping execution due to error in command {idx}")
                break

    # Format output
    output = f"📊 Execution Summary\n"
    output += f"{'=' * 50}\n"
    output += f"Total Commands: {len(commands)}\n"
    output += f"Executed: {len(results)}\n"
    output += f"Successful: {success_count}\n"
    output += f"Failed: {failed_count}\n"
    output += f"Ignore Errors: {ignore_errors}\n"
    output += f"\n"

    # Add individual command results
    for idx, result in enumerate(results, 1):
        output += f"\n{'─' * 50}\n"
        output += f"Command {idx}: {result['status']}\n"
        output += f"{'─' * 50}\n"
        output += f"📂 Working Dir: {result['working_dir']}\n"
        output += f"🔧 Command: {result['command']}\n"
        output += f"🔢 Exit Code: {result['exit_code']}\n"

        if result['stdout']:
            output += f"\n📤 STDOUT:\n{result['stdout']}\n"

        if result['stderr']:
            output += f"\n⚠️ STDERR:\n{result['stderr']}\n"

    # Final status
    output += f"\n{'=' * 50}\n"
    if failed_count == 0:
        output += "✅ All commands executed successfully\n"
        logger.info("✅ All commands executed successfully")
    elif ignore_errors:
        output += f"⚠️ Completed with {failed_count} error(s) (ignored)\n"
        logger.info(f"⚠️ Completed with {failed_count} error(s) (ignored)")
    else:
        output += f"❌ Execution stopped due to error\n"
        logger.warning("❌ Execution stopped due to error")

    return output


if __name__ == "__main__":
    # Print version information
    import mcp

    # Get Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    # Get MCP version
    mcp_version = getattr(mcp, '__version__', 'unknown')

    # Get FastMCP version (if available)
    try:
        import importlib.metadata
        fastmcp_version = importlib.metadata.version('mcp')
    except Exception:
        fastmcp_version = 'unknown'

    # Get boto3 version
    try:
        import importlib.metadata
        boto3_version = importlib.metadata.version('boto3')
    except Exception:
        boto3_version = 'unknown'

    # Print version information
    logger.info("=" * 60)
    logger.info("Skills MCP Server (AgentCore Compatible)")
    logger.info("=" * 60)
    logger.info(f"Python Version: {python_version}")
    logger.info(f"MCP Package Version: {fastmcp_version}")
    logger.info(f"boto3 Version: {boto3_version}")
    logger.info(f"Skills Directory: {SKILLS_DIR}")
    logger.info("=" * 60)

    # Run the server
    logger.info("Starting server with streamable-http transport...")
    mcp_server.run(transport="streamable-http")
