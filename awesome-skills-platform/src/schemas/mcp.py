"""
Pydantic schemas for MCP Server resources.
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any


class MCPServerBase(BaseModel):
    """Base MCP server schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    connection_type: str = Field(..., pattern="^(stdio|sse|http)$", alias="connectionType")
    endpoint: str = Field(..., min_length=1)
    config: dict[str, Any] = Field(default_factory=dict)

    class Config:
        populate_by_name = True


class MCPServerCreate(MCPServerBase):
    """Schema for creating an MCP server."""
    pass


class MCPServerUpdate(BaseModel):
    """Schema for updating an MCP server."""
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    connection_type: str | None = Field(None, pattern="^(stdio|sse|http)$", alias="connectionType")
    endpoint: str | None = Field(None, min_length=1)
    config: dict[str, Any] | None = None

    class Config:
        populate_by_name = True


class MCPServerResponse(MCPServerBase):
    """Schema for MCP server response."""
    id: str
    status: str = Field(pattern="^(online|offline|error)$")
    version: str | None = None
    agent_count: int | None = Field(None, alias="agentCount")

    class Config:
        populate_by_name = True
        from_attributes = True
