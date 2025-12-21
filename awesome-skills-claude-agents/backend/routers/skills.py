"""Skill CRUD API endpoints."""
import logging
import re
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse
from schemas.skill import (
    SkillCreateRequest,
    SkillGenerateRequest,
    SkillResponse,
    SyncResultResponse,
    SkillGenerateWithAgentRequest,
    SkillFinalizeRequest,
)
from database import db
from core.skill_manager import skill_manager
from core.agent_manager import agent_manager
from core.exceptions import (
    SkillNotFoundException,
    ValidationException,
)
from config import settings
import asyncio
import json

logger = logging.getLogger(__name__)

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
    """Upload a skill package (ZIP file).

    This will:
    1. Validate the ZIP contains SKILL.md
    2. Extract to workspace/.claude/skills/{name}/
    3. Upload extracted files to S3
    4. Save metadata to database
    """
    if not file.filename or not file.filename.endswith(".zip"):
        raise ValidationException(
            message="Invalid file format",
            detail="Skill packages must be uploaded as ZIP archives",
            suggested_action="Please ensure your file has a .zip extension and try again"
        )

    # Determine skill name
    skill_name = name or file.filename.replace(".zip", "")
    # Sanitize skill name for use as folder name
    skill_name = re.sub(r'[^a-zA-Z0-9_-]', '-', skill_name.lower())

    try:
        # Read file content
        zip_content = await file.read()

        # Upload skill package (extract to local, upload to S3)
        result = await skill_manager.upload_skill_package(
            zip_content=zip_content,
            skill_name=skill_name,
            original_filename=file.filename
        )

        # Save to database
        skill_data = {
            "name": result["name"],
            "description": result["description"],
            "version": result["version"],
            "s3_location": result["s3_location"],
            "created_by": "user",
            "is_system": False,
        }
        skill = await db.skills.put(skill_data)

        logger.info(f"Uploaded skill '{skill_name}': local={result['local_path']}, s3={result['s3_location']}")
        return skill

    except ValueError as e:
        raise ValidationException(
            message="Invalid skill package",
            detail=str(e),
            suggested_action="Ensure your ZIP contains a valid SKILL.md file"
        )
    except Exception as e:
        logger.error(f"Failed to upload skill: {e}")
        raise ValidationException(
            message="Failed to upload skill",
            detail=str(e),
            suggested_action="Please check the file and try again"
        )


@router.post("/refresh", response_model=SyncResultResponse)
async def refresh_skills():
    """Synchronize skills between local directory, S3 and database.

    This will:
    1. Scan local workspace/.claude/skills/ directory
    2. Scan S3 bucket/skills/ prefix
    3. Sync differences:
       - Local only → Upload to S3, add to DB
       - S3 only → Download to local, add to DB
       - Both exist but not in DB → Add to DB
       - DB only (orphaned) → Mark for removal
    """
    try:
        # Get current DB skills
        db_skills = await db.skills.list()

        # Run synchronization
        sync_result, skills_to_add = await skill_manager.refresh(db_skills)

        # Add new skills to database
        for skill_data in skills_to_add:
            await db.skills.put(skill_data)
            logger.info(f"Added skill to DB: {skill_data['name']}")

        # Convert to response format
        response = SyncResultResponse(
            added=sync_result.added,
            updated=sync_result.updated,
            removed=sync_result.removed,
            errors=[{"skill": e["skill"], "error": e["error"]} for e in sync_result.errors],
            total_local=sync_result.total_local,
            total_s3=sync_result.total_s3,
            total_db=sync_result.total_db,
        )

        logger.info(f"Skill refresh complete: added={len(sync_result.added)}, updated={len(sync_result.updated)}, errors={len(sync_result.errors)}")
        return response

    except Exception as e:
        logger.error(f"Failed to refresh skills: {e}")
        raise ValidationException(
            message="Failed to refresh skills",
            detail=str(e),
            suggested_action="Please check S3 connectivity and try again"
        )


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
    """Delete a skill from database, local directory and S3."""
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

    # Extract skill folder name from s3_location or name
    s3_location = skill.get("s3_location", "")
    skill_folder_name = None

    if s3_location:
        # Extract from s3://bucket/skills/name/ format
        match = re.search(r'/skills/([^/]+)/?', s3_location)
        if match:
            skill_folder_name = match.group(1)

    if not skill_folder_name:
        # Fallback: sanitize skill name
        skill_folder_name = re.sub(r'[^a-zA-Z0-9_-]', '-', skill.get("name", "").lower())

    # Delete files from local and S3
    if skill_folder_name:
        try:
            await skill_manager.delete_skill_files(skill_folder_name)
            logger.info(f"Deleted skill files for: {skill_folder_name}")
        except Exception as e:
            logger.warning(f"Failed to delete skill files for {skill_folder_name}: {e}")
            # Continue to delete from DB even if file deletion fails

    # Delete from database
    await db.skills.delete(skill_id)
    logger.info(f"Deleted skill from DB: {skill_id}")


@router.post("/generate-with-agent")
async def generate_skill_with_agent(request: Request):
    """Generate a skill using an AI agent with streaming response.

    This endpoint:
    1. Creates a specialized Skill Creator Agent
    2. Runs an interactive conversation to create the skill
    3. Agent creates files in workspace/.claude/skills/{skill_name}/
    4. Returns SSE stream of agent responses

    After this completes, call /finalize to sync to S3 and save to DB.
    """
    try:
        body = await request.json()
        skill_name = body.get("skill_name")
        skill_description = body.get("skill_description")
        session_id = body.get("session_id")
        message = body.get("message")
        model = body.get("model")

        if not skill_name:
            raise ValidationException(
                message="Missing skill_name",
                detail="skill_name is required",
                suggested_action="Provide a skill_name in the request body"
            )

        if not skill_description and not message:
            raise ValidationException(
                message="Missing skill_description or message",
                detail="Either skill_description (for initial creation) or message (for follow-up) is required",
                suggested_action="Provide skill_description for new skill or message for iteration"
            )

        # Sanitize skill name for use as folder name
        sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '-', skill_name.lower())

        logger.info(f"Starting skill generation with agent: {sanitized_name}, model: {model or 'default'}")

        async def event_generator():
            """Generate SSE events from agent conversation."""
            try:
                async for event in agent_manager.run_skill_creator_conversation(
                    skill_name=sanitized_name,
                    skill_description=skill_description or "",
                    user_message=message,
                    session_id=session_id,
                    model=model,
                ):
                    yield f"data: {json.dumps(event)}\n\n"
            except asyncio.CancelledError:
                logger.info("Client disconnected from skill generation stream")
                raise
            except Exception as e:
                logger.error(f"Error in skill generation stream: {e}")
                error_event = {
                    "type": "error",
                    "error": str(e),
                }
                yield f"data: {json.dumps(error_event)}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Failed to start skill generation: {e}")
        raise ValidationException(
            message="Failed to start skill generation",
            detail=str(e),
            suggested_action="Please check your request and try again"
        )


@router.post("/finalize", response_model=SkillResponse, status_code=201)
async def finalize_skill(request: SkillFinalizeRequest):
    """Finalize skill creation by syncing to S3 and saving to database.

    This endpoint:
    1. Validates the skill directory exists locally
    2. Extracts metadata from SKILL.md
    3. Uploads to S3
    4. Saves metadata to database

    Call this after generate-with-agent completes successfully.
    """
    # Sanitize skill name
    skill_name = re.sub(r'[^a-zA-Z0-9_-]', '-', request.skill_name.lower())

    logger.info(f"Finalizing skill: original='{request.skill_name}', sanitized='{skill_name}'")

    # Check if skill directory exists
    skills_dir = Path(settings.agent_workspace_dir) / ".claude" / "skills"
    skill_path = skills_dir / skill_name

    logger.info(f"Looking for skill at: {skill_path}, exists: {skill_path.exists()}")

    if not skill_path.exists():
        # List available directories for debugging
        available = [d.name for d in skills_dir.iterdir() if d.is_dir()] if skills_dir.exists() else []
        logger.error(f"Skill directory not found. Available directories: {available}")
        raise ValidationException(
            message="Skill directory not found",
            detail=f"Expected skill at: {skill_path}. Available: {available}",
            suggested_action="Ensure the skill was created successfully before finalizing"
        )

    skill_md_path = skill_path / "SKILL.md"
    if not skill_md_path.exists():
        raise ValidationException(
            message="SKILL.md not found",
            detail=f"Skill directory exists but missing SKILL.md at: {skill_md_path}",
            suggested_action="Ensure the agent created a valid SKILL.md file"
        )

    try:
        # Extract metadata from SKILL.md
        metadata = skill_manager.extract_skill_metadata(skill_path)

        # Upload to S3 (note: parameter order is skill_name, skill_dir)
        s3_location = await skill_manager.upload_directory_to_s3(skill_name, skill_path)

        # Save to database (metadata is a SkillMetadata object, not a dict)
        skill_data = {
            "name": metadata.name or skill_name,
            "description": metadata.description or "",
            "version": metadata.version or "1.0.0",
            "s3_location": s3_location,
            "created_by": "ai-agent",
            "is_system": False,
        }
        skill = await db.skills.put(skill_data)

        logger.info(f"Finalized skill '{skill_name}': s3={s3_location}")
        return skill

    except Exception as e:
        logger.error(f"Failed to finalize skill: {e}")
        raise ValidationException(
            message="Failed to finalize skill",
            detail=str(e),
            suggested_action="Please check the skill files and try again"
        )
