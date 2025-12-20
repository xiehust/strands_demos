"""
Unit tests for Skill Tool module.
"""
import os
import pytest
from unittest.mock import patch, MagicMock, mock_open


class TestInitSkills:
    """Tests for init_skills function."""

    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_init_skills_empty_directory(self, mock_isdir, mock_listdir):
        """Test init_skills with empty skills directory."""
        mock_listdir.return_value = []

        from src.skill_tool import init_skills

        result = init_skills()
        assert result == ""

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_init_skills_with_valid_skill(self, mock_isdir, mock_listdir, mock_file):
        """Test init_skills with a valid skill."""
        mock_listdir.return_value = ["xlsx"]
        mock_isdir.return_value = True

        skill_content = """---
name: xlsx
description: Excel file processing skill
---
# XLSX Skill

This skill handles Excel files.
"""
        mock_file.return_value.read.return_value = skill_content

        from src.skill_tool import init_skills

        result = init_skills()

        assert "<skill>" in result
        assert "<name>" in result
        assert "xlsx" in result
        assert "Excel file processing skill" in result

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_init_skills_skips_hidden_dirs(self, mock_isdir, mock_listdir, mock_file):
        """Test init_skills skips hidden directories."""
        mock_listdir.return_value = [".hidden", "xlsx"]
        mock_isdir.return_value = True

        skill_content = """---
name: xlsx
description: Excel skill
---
Content
"""
        mock_file.return_value.read.return_value = skill_content

        from src.skill_tool import init_skills

        # Should only process xlsx, not .hidden
        result = init_skills()
        assert "xlsx" in result
        assert ".hidden" not in result

    @patch("builtins.open")
    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_init_skills_invalid_yaml(self, mock_isdir, mock_listdir, mock_file):
        """Test init_skills with invalid YAML frontmatter."""
        mock_listdir.return_value = ["invalid_skill"]
        mock_isdir.return_value = True

        # Missing YAML frontmatter
        mock_file.return_value.__enter__.return_value.read.return_value = "Just content, no frontmatter"

        from src.skill_tool import init_skills

        result = init_skills()
        # Should skip invalid skill
        assert "invalid_skill" not in result or result == ""


class TestLoadSkill:
    """Tests for load_skill function."""

    @patch("builtins.open", new_callable=mock_open)
    def test_load_skill_success(self, mock_file):
        """Test successful skill loading."""
        skill_content = """---
name: xlsx
description: Excel skill
---
# XLSX Skill Instructions

Process Excel files here.
"""
        mock_file.return_value.read.return_value = skill_content

        from src.skill_tool import load_skill

        result = load_skill("xlsx")

        assert len(result) == 2
        assert "skill is running" in result[0]["text"]
        assert "xlsx" in result[0]["text"]
        assert "# XLSX Skill Instructions" in result[1]["text"]

    @patch("builtins.open")
    def test_load_skill_file_not_found(self, mock_file):
        """Test load_skill with non-existent skill."""
        mock_file.side_effect = FileNotFoundError("Skill not found")

        from src.skill_tool import load_skill

        result = load_skill("nonexistent")

        assert len(result) == 1
        assert "failed" in result[0]["text"]

    @patch("builtins.open", new_callable=mock_open)
    def test_load_skill_invalid_format(self, mock_file):
        """Test load_skill with invalid skill format."""
        mock_file.return_value.read.return_value = "No YAML frontmatter"

        from src.skill_tool import load_skill

        result = load_skill("invalid")

        assert len(result) == 1
        assert "failed" in result[0]["text"]


class TestGenerateSkillTool:
    """Tests for generate_skill_tool function."""

    @patch("src.skill_tool.init_skills")
    def test_generate_skill_tool_no_skills(self, mock_init):
        """Test generate_skill_tool with no skills available."""
        mock_init.return_value = ""

        from src.skill_tool import generate_skill_tool

        result = generate_skill_tool()
        assert result is None

    @patch("src.skill_tool.init_skills")
    def test_generate_skill_tool_with_skills(self, mock_init):
        """Test generate_skill_tool with skills available."""
        mock_init.return_value = "<skill><name>xlsx</name></skill>"

        from src.skill_tool import generate_skill_tool

        result = generate_skill_tool()

        assert result is not None
        assert callable(result)
        assert result.__name__ == "Skill"
        assert "xlsx" in result.__doc__


class TestSkillToolInterceptor:
    """Tests for SkillToolInterceptor class."""

    def test_init(self):
        """Test SkillToolInterceptor initialization."""
        from src.skill_tool import SkillToolInterceptor

        interceptor = SkillToolInterceptor()
        assert interceptor.tooluse_ids == {}

    def test_register_hooks(self):
        """Test hook registration."""
        from src.skill_tool import SkillToolInterceptor

        interceptor = SkillToolInterceptor()

        mock_registry = MagicMock()
        interceptor.register_hooks(mock_registry)

        # Should register 3 callbacks
        assert mock_registry.add_callback.call_count == 3

    @patch("src.skill_tool.load_skill")
    def test_add_skill_content_for_skill_tool(self, mock_load):
        """Test add_skill_content handles Skill tool calls."""
        from src.skill_tool import SkillToolInterceptor

        mock_load.return_value = [{"text": "skill content"}]

        interceptor = SkillToolInterceptor()

        event = MagicMock()
        event.tool_use = {
            "name": "Skill",
            "input": {"command": "xlsx"},
            "toolUseId": "tool-123"
        }

        interceptor.add_skill_content(event)

        assert "tool-123" in interceptor.tooluse_ids
        mock_load.assert_called_once_with("xlsx")

    def test_add_skill_content_ignores_other_tools(self):
        """Test add_skill_content ignores non-Skill tools."""
        from src.skill_tool import SkillToolInterceptor

        interceptor = SkillToolInterceptor()

        event = MagicMock()
        event.tool_use = {
            "name": "OtherTool",
            "input": {},
            "toolUseId": "tool-456"
        }

        interceptor.add_skill_content(event)

        assert "tool-456" not in interceptor.tooluse_ids

    def test_add_skill_message(self):
        """Test add_skill_message injects skill content."""
        from src.skill_tool import SkillToolInterceptor

        interceptor = SkillToolInterceptor()
        interceptor.tooluse_ids["tool-123"] = [{"text": "skill content"}]

        event = MagicMock()
        event.message = {
            "role": "user",
            "content": [
                {"toolResult": {"toolUseId": "tool-123"}}
            ]
        }

        interceptor.add_skill_message(event)

        # Skill content should be added
        assert len(event.message["content"]) > 1
        assert "tool-123" not in interceptor.tooluse_ids  # Cleaned up

    def test_add_message_cache(self):
        """Test add_message_cache adds cache point."""
        from src.skill_tool import SkillToolInterceptor

        interceptor = SkillToolInterceptor()

        mock_agent = MagicMock()
        mock_agent.messages = [
            {"content": [{"text": "message 1"}]},
            {"content": [{"text": "message 2"}]},
        ]

        event = MagicMock()
        event.agent = mock_agent

        interceptor.add_message_cache(event)

        # Last message should have cachePoint
        last_content = mock_agent.messages[-1]["content"]
        assert any("cachePoint" in item for item in last_content)
