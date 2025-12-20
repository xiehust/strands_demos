"""Skill CRUD API endpoints."""
from fastapi import APIRouter, UploadFile, File, Form
from schemas.skill import SkillCreateRequest, SkillGenerateRequest, SkillResponse
from database import db
from core.exceptions import (
    SkillNotFoundException,
    ValidationException,
)
import asyncio

router = APIRouter()


@router.get("", response_model=list[SkillResponse])
async def list_skills():
    """List all skills."""
    return await db.skills.list()


@router.get("/system", response_model=list[SkillResponse])
async def list_system_skills():
    """List system-provided skills."""
    skills = await db.skills.list()
    return [s for s in skills if s.get("is_system", False)]


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: str):
    """Get a specific skill by ID."""
    skill = await db.skills.get(skill_id)
    if not skill:
        raise SkillNotFoundException(
            detail=f"Skill with ID '{skill_id}' does not exist",
            suggested_action="Please check the skill ID and try again"
        )
    return skill


@router.post("/upload", response_model=SkillResponse, status_code=201)
async def upload_skill(
    file: UploadFile = File(...),
    name: str = Form(None),
):
    """Upload a skill package (ZIP file)."""
    if not file.filename or not file.filename.endswith(".zip"):
        raise ValidationException(
            message="Invalid file format",
            detail="Skill packages must be uploaded as ZIP archives",
            suggested_action="Please ensure your file has a .zip extension and try again"
        )

    # In production, this would:
    # 1. Upload to S3
    # 2. Extract and validate SKILL.md
    # 3. Store metadata in DynamoDB

    skill_name = name or file.filename.replace(".zip", "")
    skill_data = {
        "name": skill_name,
        "description": f"Uploaded skill package: {file.filename}",
        "created_by": "user",
        "version": "1.0.0",
        "is_system": False,
        "s3_location": f"s3://agent-platform-skills/{skill_name}.zip",
    }
    skill = await db.skills.put(skill_data)
    return skill


@router.post("/generate", response_model=SkillResponse, status_code=201)
async def generate_skill(request: SkillGenerateRequest):
    """Generate a skill using AI."""
    # Simulate AI generation delay
    await asyncio.sleep(1)

    # Generate skill name from description
    words = request.description.split()[:2]
    skill_name = "".join(w.capitalize() for w in words) or "NewSkill"

    skill_data = {
        "name": skill_name,
        "description": request.description,
        "created_by": "ai-agent",
        "version": "1.0.0",
        "is_system": False,
    }
    skill = await db.skills.put(skill_data)
    return skill


@router.delete("/{skill_id}", status_code=204)
async def delete_skill(skill_id: str):
    """Delete a skill."""
    skill = await db.skills.get(skill_id)
    if not skill:
        raise SkillNotFoundException(
            detail=f"Skill with ID '{skill_id}' does not exist",
            suggested_action="Please check the skill ID and try again"
        )

    if skill.get("is_system", False):
        raise ValidationException(
            message="Cannot delete system skill",
            detail="System skills are protected and cannot be deleted",
            suggested_action="Only user-created skills can be deleted"
        )

    await db.skills.delete(skill_id)
