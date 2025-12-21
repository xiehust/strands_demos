"""Agent CRUD API endpoints."""
from fastapi import APIRouter
from schemas.agent import AgentCreateRequest, AgentUpdateRequest, AgentResponse
from database import db
from config import ANTHROPIC_TO_BEDROCK_MODEL_MAP
from core.exceptions import (
    AgentNotFoundException,
    ValidationException,
)

router = APIRouter()


@router.get("/models", response_model=list[str])
async def list_available_models():
    """List all available Claude models.

    Returns the Anthropic model IDs that have Bedrock mappings configured.
    """
    return list(ANTHROPIC_TO_BEDROCK_MODEL_MAP.keys())


@router.get("", response_model=list[AgentResponse])
async def list_agents():
    """List all agents."""
    agents = await db.agents.list()
    # Filter out the default agent from the list
    return [a for a in agents if a.get("id") != "default"]


@router.get("/default", response_model=AgentResponse)
async def get_default_agent():
    """Get the default system agent."""
    agent = await db.agents.get("default")
    if not agent:
        raise AgentNotFoundException(
            detail="Default agent configuration is missing",
            suggested_action="Contact the administrator to set up the default agent"
        )
    return agent


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get a specific agent by ID."""
    agent = await db.agents.get(agent_id)
    if not agent:
        raise AgentNotFoundException(
            detail=f"Agent with ID '{agent_id}' does not exist",
            suggested_action="Please check the agent ID and try again"
        )
    return agent


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(request: AgentCreateRequest):
    """Create a new agent."""
    agent_data = {
        "name": request.name,
        "description": request.description,
        "model": request.model,
        "permission_mode": request.permission_mode,
        "max_turns": request.max_turns,
        "system_prompt": request.system_prompt,
        "allowed_tools": request.allowed_tools,
        "skill_ids": request.skill_ids,
        "mcp_ids": request.mcp_ids,
        "working_directory": None,  # Use default from settings.agent_workspace_dir
        "enable_bash_tool": request.enable_bash_tool,
        "enable_file_tools": request.enable_file_tools,
        "enable_web_tools": request.enable_web_tools,
        "enable_tool_logging": True,
        "enable_safety_checks": True,
        "status": "active",
    }
    agent = await db.agents.put(agent_data)
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, request: AgentUpdateRequest):
    """Update an existing agent."""
    existing = await db.agents.get(agent_id)
    if not existing:
        raise AgentNotFoundException(
            detail=f"Agent with ID '{agent_id}' does not exist",
            suggested_action="Please check the agent ID and try again"
        )

    updates = request.model_dump(exclude_unset=True)
    agent = await db.agents.update(agent_id, updates)
    return agent


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str):
    """Delete an agent."""
    if agent_id == "default":
        raise ValidationException(
            message="Cannot delete the default agent",
            detail="The default agent is a system resource and cannot be deleted",
            suggested_action="If you need to modify the default agent, use the update endpoint instead"
        )

    deleted = await db.agents.delete(agent_id)
    if not deleted:
        raise AgentNotFoundException(
            detail=f"Agent with ID '{agent_id}' does not exist",
            suggested_action="Please check the agent ID and try again"
        )
