"""
Pydantic schemas for Skill resources.
"""
from datetime import datetime
from pydantic import BaseModel, Field


class SkillBase(BaseModel):
    """Base skill schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    version: str = Field("1.0.0", pattern=r'^\d+\.\d+\.\d+$')
    is_system: bool = Field(False, alias="isSystem")

    class Config:
        populate_by_name = True


class SkillCreate(SkillBase):
    """Schema for creating a skill."""
    pass


class SkillUpdate(BaseModel):
    """Schema for updating a skill."""
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=500)
    version: str | None = Field(None, pattern=r'^\d+\.\d+\.\d+$')

    class Config:
        populate_by_name = True


class SkillResponse(SkillBase):
    """Schema for skill response."""
    id: str
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        from_attributes = True
