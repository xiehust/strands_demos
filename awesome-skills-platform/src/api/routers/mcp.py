"""
MCP Server management API endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from src.schemas.mcp import MCPServerCreate, MCPServerUpdate, MCPServerResponse
from src.database.dynamodb import db_client

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.post("", response_model=MCPServerResponse, status_code=status.HTTP_201_CREATED)
def create_mcp_server(mcp_server: MCPServerCreate):
    """Create a new MCP server configuration."""
    mcp_data = mcp_server.model_dump(by_alias=True, exclude_unset=True)
    created_mcp = db_client.create_mcp_server(mcp_data)
    return MCPServerResponse(**created_mcp)


@router.get("", response_model=List[MCPServerResponse])
def list_mcp_servers():
    """List all MCP servers."""
    mcp_servers = db_client.list_mcp_servers()
    return [MCPServerResponse(**mcp) for mcp in mcp_servers]


@router.get("/{mcp_id}", response_model=MCPServerResponse)
def get_mcp_server(mcp_id: str):
    """Get an MCP server by ID."""
    mcp_server = db_client.get_mcp_server(mcp_id)
    if not mcp_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCP server with id {mcp_id} not found"
        )
    return MCPServerResponse(**mcp_server)


@router.put("/{mcp_id}", response_model=MCPServerResponse)
def update_mcp_server(mcp_id: str, mcp_server: MCPServerUpdate):
    """Update an MCP server configuration."""
    # Check if MCP server exists
    existing_mcp = db_client.get_mcp_server(mcp_id)
    if not existing_mcp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCP server with id {mcp_id} not found"
        )

    # Update MCP server
    mcp_data = mcp_server.model_dump(by_alias=True, exclude_unset=True)
    updated_mcp = db_client.update_mcp_server(mcp_id, mcp_data)

    if not updated_mcp:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update MCP server"
        )

    return MCPServerResponse(**updated_mcp)


@router.delete("/{mcp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mcp_server(mcp_id: str):
    """Delete an MCP server."""
    # Check if MCP server exists
    existing_mcp = db_client.get_mcp_server(mcp_id)
    if not existing_mcp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCP server with id {mcp_id} not found"
        )

    # Delete MCP server
    success = db_client.delete_mcp_server(mcp_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete MCP server"
        )
