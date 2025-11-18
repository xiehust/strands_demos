"""
Agent management API endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from src.schemas.agent import AgentCreate, AgentUpdate, AgentResponse
from src.database.dynamodb import db_client

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(agent: AgentCreate):
    """Create a new agent."""
    agent_data = agent.model_dump(by_alias=True, exclude_unset=True)
    created_agent = db_client.create_agent(agent_data)
    return AgentResponse(**created_agent)


@router.get("", response_model=List[AgentResponse])
def list_agents():
    """List all agents."""
    agents = db_client.list_agents()
    return [AgentResponse(**agent) for agent in agents]


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str):
    """Get an agent by ID."""
    agent = db_client.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )
    return AgentResponse(**agent)


@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: str, agent: AgentUpdate):
    """Update an agent."""
    # Check if agent exists
    existing_agent = db_client.get_agent(agent_id)
    if not existing_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )

    # Update agent
    agent_data = agent.model_dump(by_alias=True, exclude_unset=True)
    updated_agent = db_client.update_agent(agent_id, agent_data)

    if not updated_agent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update agent"
        )

    return AgentResponse(**updated_agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: str):
    """Delete an agent."""
    # Check if agent exists
    existing_agent = db_client.get_agent(agent_id)
    if not existing_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )

    # Delete agent
    success = db_client.delete_agent(agent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete agent"
        )
