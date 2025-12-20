"""Chat SSE streaming API endpoints."""
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from schemas.message import ChatRequest, ChatSessionResponse
from database import db
from core.agent_manager import agent_manager
from core.exceptions import (
    AgentNotFoundException,
    SessionNotFoundException,
    ValidationException,
    AgentExecutionException,
    AgentTimeoutException,
)
import json
import asyncio


router = APIRouter()


def create_sse_error(code: str, message: str, detail: str = None, suggested_action: str = None) -> str:
    """Create an SSE-formatted error event."""
    error_data = {
        "type": "error",
        "code": code,
        "message": message,
    }
    if detail:
        error_data["detail"] = detail
    if suggested_action:
        error_data["suggested_action"] = suggested_action
    return f"data: {json.dumps(error_data)}\n\n"


@router.post("/stream")
async def chat_stream(request: Request):
    """Stream chat responses via SSE."""
    try:
        body = await request.json()
        chat_request = ChatRequest(**body)
    except json.JSONDecodeError as e:
        raise ValidationException(
            message="Invalid JSON format",
            detail=f"Failed to parse request body: {str(e)}",
        )
    except Exception as e:
        raise ValidationException(
            message="Invalid request data",
            detail=str(e),
        )

    # Verify agent exists
    agent = await db.agents.get(chat_request.agent_id)
    if not agent:
        raise AgentNotFoundException(
            detail=f"Agent with ID '{chat_request.agent_id}' does not exist",
            suggested_action="Please check the agent ID and try again"
        )

    async def generate():
        try:
            async for msg in agent_manager.run_conversation(
                agent_id=chat_request.agent_id,
                user_message=chat_request.message,
                session_id=chat_request.session_id,
                enable_skills=chat_request.enable_skills,
                enable_mcp=chat_request.enable_mcp,
            ):
                yield f"data: {json.dumps(msg)}\n\n"
        except asyncio.TimeoutError:
            yield create_sse_error(
                code="AGENT_TIMEOUT",
                message="Agent response timed out. Your conversation has been saved.",
                suggested_action="Please try again"
            )
        except Exception as e:
            error_message = str(e)
            # Determine error type and provide appropriate response
            if "timeout" in error_message.lower():
                yield create_sse_error(
                    code="AGENT_TIMEOUT",
                    message="Agent response timed out. Your conversation has been saved.",
                    suggested_action="Please try again"
                )
            elif "connection" in error_message.lower() or "network" in error_message.lower():
                yield create_sse_error(
                    code="SERVICE_UNAVAILABLE",
                    message="Unable to connect to the AI service",
                    detail=error_message,
                    suggested_action="Please check your connection and try again"
                )
            else:
                yield create_sse_error(
                    code="AGENT_EXECUTION_ERROR",
                    message="Agent execution failed",
                    detail=error_message,
                    suggested_action="Please try again or contact support"
                )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(agent_id: str | None = None):
    """List chat sessions."""
    sessions = await db.sessions.list()
    if agent_id:
        sessions = [s for s in sessions if s.get("agent_id") == agent_id]
    return sessions


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str):
    """Delete a chat session."""
    deleted = await db.sessions.delete(session_id)
    if not deleted:
        raise SessionNotFoundException(
            detail=f"Session with ID '{session_id}' does not exist",
            suggested_action="Please check the session ID and try again"
        )
