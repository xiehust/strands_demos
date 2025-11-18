"""
Skill management API endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from src.schemas.skill import SkillCreate, SkillUpdate, SkillResponse
from src.database.dynamodb import db_client

router = APIRouter(prefix="/skills", tags=["skills"])


@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(skill: SkillCreate):
    """Create a new skill."""
    skill_data = skill.model_dump(by_alias=True, exclude_unset=True)
    created_skill = db_client.create_skill(skill_data)
    return SkillResponse(**created_skill)


@router.get("", response_model=List[SkillResponse])
def list_skills():
    """List all skills."""
    skills = db_client.list_skills()
    return [SkillResponse(**skill) for skill in skills]


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(skill_id: str):
    """Get a skill by ID."""
    skill = db_client.get_skill(skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with id {skill_id} not found"
        )
    return SkillResponse(**skill)


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(skill_id: str):
    """Delete a skill."""
    # Check if skill exists
    existing_skill = db_client.get_skill(skill_id)
    if not existing_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with id {skill_id} not found"
        )

    # Delete skill
    success = db_client.delete_skill(skill_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete skill"
        )
