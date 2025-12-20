"""Skill-related Pydantic models."""
from pydantic import BaseModel, Field
from datetime import datetime


class SkillMetadata(BaseModel):
    """Skill metadata model."""

    id: str | None = None
    name: str = Field(..., min_length=1, max_length=255)
    description: str
    s3_location: str | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    version: str = Field(default="1.0.0")
    is_system: bool = Field(default=False)


class SkillCreateRequest(BaseModel):
    """Request model for creating a skill via AI generation."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(
        ..., description="Natural language description of the skill to generate"
    )
    examples: list[str] | None = None


class SkillGenerateRequest(BaseModel):
    """Request model for generating a skill with AI."""

    description: str = Field(
        ..., description="Natural language description of the skill to generate"
    )
    examples: list[str] | None = None


class SkillResponse(BaseModel):
    """Response model for skill."""

    id: str
    name: str
    description: str
    s3_location: str | None = None
    created_by: str
    created_at: str
    updated_at: str
    version: str
    is_system: bool
