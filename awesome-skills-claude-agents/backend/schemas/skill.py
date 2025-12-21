"""Skill-related Pydantic models."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


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


class SyncError(BaseModel):
    """Error detail for sync operation."""
    skill: str
    error: str


class SyncResultResponse(BaseModel):
    """Response model for skill synchronization."""
    added: list[str] = Field(default_factory=list, description="Skills added during sync")
    updated: list[str] = Field(default_factory=list, description="Skills updated during sync")
    removed: list[str] = Field(default_factory=list, description="Orphaned DB records found")
    errors: list[SyncError] = Field(default_factory=list, description="Errors encountered during sync")
    total_local: int = Field(default=0, description="Total skills found in local directory")
    total_s3: int = Field(default=0, description="Total skills found in S3")
    total_db: int = Field(default=0, description="Total skills in database before sync")


class SkillGenerateWithAgentRequest(BaseModel):
    """Request model for generating a skill with agent conversation."""

    skill_name: str = Field(..., min_length=1, max_length=255, description="Name of the skill to create")
    skill_description: str = Field(..., description="Description of what the skill should do")
    session_id: Optional[str] = Field(None, description="Session ID for continuing conversation")
    message: Optional[str] = Field(None, description="Follow-up message for iterating on the skill")
    model: Optional[str] = Field(None, description="Model to use for skill generation (e.g., claude-sonnet-4-5-20250514)")


class SkillFinalizeRequest(BaseModel):
    """Request model for finalizing skill creation."""

    skill_name: str = Field(..., min_length=1, max_length=255, description="Name of the skill to finalize")

