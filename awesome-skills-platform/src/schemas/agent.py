"""
Pydantic schemas for Agent resources.
"""
from datetime import datetime
from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    """Base agent schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    model_id: str = Field(..., alias="modelId")
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(4096, ge=256, le=200000, alias="maxTokens")
    thinking_enabled: bool = Field(False, alias="thinkingEnabled")
    thinking_budget: int = Field(1024, ge=256, le=10000, alias="thinkingBudget")
    system_prompt: str | None = Field(None, max_length=5000, alias="systemPrompt")
    skill_ids: list[str] = Field(default_factory=list, alias="skillIds")
    mcp_ids: list[str] = Field(default_factory=list, alias="mcpIds")
    status: str = Field("active", pattern="^(active|inactive)$")

    class Config:
        populate_by_name = True


class AgentCreate(AgentBase):
    """Schema for creating an agent."""
    pass


class AgentUpdate(BaseModel):
    """Schema for updating an agent (all fields optional)."""
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    model_id: str | None = Field(None, alias="modelId")
    temperature: float | None = Field(None, ge=0.0, le=1.0)
    max_tokens: int | None = Field(None, ge=256, le=200000, alias="maxTokens")
    thinking_enabled: bool | None = Field(None, alias="thinkingEnabled")
    thinking_budget: int | None = Field(None, ge=256, le=10000, alias="thinkingBudget")
    system_prompt: str | None = Field(None, max_length=5000, alias="systemPrompt")
    skill_ids: list[str] | None = Field(None, alias="skillIds")
    mcp_ids: list[str] | None = Field(None, alias="mcpIds")
    status: str | None = Field(None, pattern="^(active|inactive)$")

    class Config:
        populate_by_name = True


class AgentResponse(AgentBase):
    """Schema for agent response."""
    id: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True
