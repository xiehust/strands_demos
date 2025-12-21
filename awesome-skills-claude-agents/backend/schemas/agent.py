"""Agent-related Pydantic models."""
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class AgentConfig(BaseModel):
    """Agent configuration model."""

    id: str | None = None
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    model: str | None = Field(
        default=None, description="Claude model to use (defaults to Claude Code default)"
    )
    permission_mode: Literal["default", "acceptEdits", "plan", "bypassPermissions"] = "default"
    max_turns: int | None = Field(default=None, ge=1, le=100)
    system_prompt: str | None = None
    allowed_tools: list[str] = Field(default_factory=list)
    skill_ids: list[str] = Field(default_factory=list)
    mcp_ids: list[str] = Field(default_factory=list)
    working_directory: str | None = Field(default=None, description="Working directory for the agent (defaults to settings.agent_workspace_dir)")
    enable_bash_tool: bool = True
    enable_file_tools: bool = True
    enable_web_tools: bool = False
    enable_tool_logging: bool = True
    enable_safety_checks: bool = True
    status: Literal["active", "inactive"] = "active"
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Data Analyst Agent",
                "description": "Specialized in data analysis and visualization",
                "model": "sonnet",
                "permission_mode": "acceptEdits",
                "max_turns": 20,
                "skill_ids": ["xlsx-skill", "docx-skill"],
                "mcp_ids": ["postgres-mcp"],
                "enable_web_tools": True,
            }
        }


class AgentCreateRequest(BaseModel):
    """Request model for creating an agent."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    model: str | None = None
    permission_mode: Literal["default", "acceptEdits", "plan", "bypassPermissions"] = "default"
    max_turns: int | None = Field(default=100, ge=1, le=100)
    system_prompt: str | None = None
    allowed_tools: list[str] = Field(default_factory=list)
    skill_ids: list[str] = Field(default_factory=list)
    mcp_ids: list[str] = Field(default_factory=list)
    enable_bash_tool: bool = True
    enable_file_tools: bool = True
    enable_web_tools: bool = False


class AgentUpdateRequest(BaseModel):
    """Request model for updating an agent."""

    name: str | None = None
    description: str | None = None
    model: str | None = None
    permission_mode: Literal["default", "acceptEdits", "plan", "bypassPermissions"] | None = None
    max_turns: int | None = None
    system_prompt: str | None = None
    allowed_tools: list[str] | None = None
    skill_ids: list[str] | None = None
    mcp_ids: list[str] | None = None
    enable_bash_tool: bool | None = None
    enable_file_tools: bool | None = None
    enable_web_tools: bool | None = None
    enable_tool_logging: bool | None = None
    enable_safety_checks: bool | None = None
    status: Literal["active", "inactive"] | None = None


class AgentResponse(BaseModel):
    """Response model for agent."""

    id: str
    name: str
    description: str | None = None
    model: str | None = None
    permission_mode: str
    max_turns: int | None = None
    system_prompt: str | None = None
    allowed_tools: list[str]
    skill_ids: list[str]
    mcp_ids: list[str]
    working_directory: str | None
    enable_bash_tool: bool
    enable_file_tools: bool
    enable_web_tools: bool
    enable_tool_logging: bool
    enable_safety_checks: bool
    status: str
    created_at: str
    updated_at: str
