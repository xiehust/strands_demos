"""
Chat API endpoints for synchronous and streaming conversations.
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from datetime import datetime
import uuid
import logging
import json

from src.schemas.chat import ChatRequest, ChatResponse, Conversation, ChatMessage
from src.core.agent_manager import agent_manager

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

# In-memory conversation storage (lightweight cache, AgentCore Memory handles persistence)
_conversations: dict[str, Conversation] = {}


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_message(request: ChatRequest):
    """
    Send a message to an agent and get a synchronous response.

    Args:
        request: ChatRequest containing agent_id, message, and optional conversation_id

    Returns:
        ChatResponse with the agent's reply
    """
    try:
        # Generate or use existing conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Log request
        logger.info(f"Chat request - Agent: {request.agent_id}, Conversation: {conversation_id}")

        # Run agent with memory session (conversation_id serves as session_id)
        result = await agent_manager.run_async(
            agent_id=request.agent_id,
            user_message=request.message,
            session_id=conversation_id,  # Enable memory persistence
            actor_id="default-user",  # TODO: Replace with actual user ID when auth is implemented
        )

        # Create response
        timestamp = datetime.utcnow()
        response = ChatResponse(
            agentId=request.agent_id,
            conversationId=conversation_id,
            message=result["message"],
            thinking=result.get("thinking"),
            modelId=result["model_id"],
            stopReason=result.get("stop_reason"),
            timestamp=timestamp,
        )

        # Store conversation in memory (simplified for Phase 4)
        if conversation_id not in _conversations:
            _conversations[conversation_id] = Conversation(
                id=conversation_id,
                agentId=request.agent_id,
                title=request.message[:50] + "..." if len(request.message) > 50 else request.message,
                messages=[],
                createdAt=timestamp,
                updatedAt=timestamp,
            )

        # Add messages to conversation
        conversation = _conversations[conversation_id]
        conversation.messages.append(ChatMessage(
            role="user",
            content=request.message,
            timestamp=timestamp,
        ))
        conversation.messages.append(ChatMessage(
            role="assistant",
            content=result["message"],
            thinking=result.get("thinking"),
            timestamp=timestamp,
        ))
        conversation.updated_at = timestamp

        logger.info(f"Chat response sent - {len(result['message'])} chars")

        return response

    except ValueError as e:
        # Agent not found
        logger.error(f"Agent not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        # Other errors
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )


@router.post("/stream")
async def stream_message(request: ChatRequest):
    """
    Send a message to an agent and get a streaming response using Server-Sent Events (SSE).

    Args:
        request: ChatRequest containing agent_id, message, and optional conversation_id

    Returns:
        StreamingResponse with SSE format
    """
    async def generate_sse_stream():
        """Generate Server-Sent Events stream."""
        try:
            # Generate or use existing conversation ID
            conversation_id = request.conversation_id or str(uuid.uuid4())
            timestamp = datetime.utcnow()

            # Log request
            logger.info(f"Streaming chat request - Agent: {request.agent_id}, Conversation: {conversation_id}")

            # Send conversation metadata
            yield f"data: {json.dumps({'type': 'start', 'conversationId': conversation_id, 'agentId': request.agent_id})}\n\n"

            # Get agent with memory session (conversation_id serves as session_id)
            agent = agent_manager.get_or_create_agent(
                agent_id=request.agent_id,
                session_id=conversation_id,  # Enable memory persistence
                actor_id="default-user",  # TODO: Replace with actual user ID when auth is implemented
            )

            # Stream agent response
            accumulated_text = ""
            accumulated_thinking = []

            async for event in agent.stream_async(request.message):
                # Event format from Strands: {'data': 'text chunk'} or {'thinking': 'thinking content'}
                if "data" in event:
                    chunk = event["data"]
                    accumulated_text += chunk
                    # Send text chunk
                    yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"

                elif "thinking" in event:
                    thinking_content = event["thinking"]
                    accumulated_thinking.append(thinking_content)
                    # Send thinking chunk
                    yield f"data: {json.dumps({'type': 'thinking', 'content': thinking_content})}\n\n"

                elif "tool_use" in event:
                    # Send tool use event
                    tool_use = event["tool_use"]
                    yield f"data: {json.dumps({'type': 'tool_use', 'tool': tool_use})}\n\n"

                elif "tool_result" in event:
                    # Send tool result event
                    tool_result = event["tool_result"]
                    yield f"data: {json.dumps({'type': 'tool_result', 'result': tool_result})}\n\n"

            # Send completion event
            cache_key = f"{request.agent_id}:{conversation_id}"
            model_id = agent_manager._agents[cache_key]["model_id"]
            yield f"data: {json.dumps({'type': 'done', 'modelId': model_id})}\n\n"

            # Store conversation in memory
            if conversation_id not in _conversations:
                _conversations[conversation_id] = Conversation(
                    id=conversation_id,
                    agentId=request.agent_id,
                    title=request.message[:50] + "..." if len(request.message) > 50 else request.message,
                    messages=[],
                    createdAt=timestamp,
                    updatedAt=timestamp,
                )

            # Add messages to conversation
            conversation = _conversations[conversation_id]
            conversation.messages.append(ChatMessage(
                role="user",
                content=request.message,
                timestamp=timestamp,
            ))
            conversation.messages.append(ChatMessage(
                role="assistant",
                content=accumulated_text,
                thinking=accumulated_thinking if accumulated_thinking else None,
                timestamp=datetime.utcnow(),
            ))
            conversation.updated_at = datetime.utcnow()

            logger.info(f"Streaming complete - {len(accumulated_text)} chars")

        except ValueError as e:
            # Agent not found
            logger.error(f"Agent not found: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        except Exception as e:
            # Other errors
            logger.error(f"Streaming error: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': f'Failed to process request: {str(e)}'})}\n\n"

    return StreamingResponse(
        generate_sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.get("/conversations", response_model=list[Conversation])
def list_conversations():
    """
    List all conversations.

    Returns:
        List of conversations
    """
    return list(_conversations.values())


@router.get("/conversations/{conversation_id}", response_model=Conversation)
def get_conversation(conversation_id: str):
    """
    Get a specific conversation by ID.

    Args:
        conversation_id: The conversation ID

    Returns:
        Conversation with messages
    """
    conversation = _conversations.get(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )
    return conversation


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: str):
    """
    Delete a conversation.

    Args:
        conversation_id: The conversation ID to delete
    """
    if conversation_id not in _conversations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    del _conversations[conversation_id]
    logger.info(f"Deleted conversation {conversation_id}")


@router.post("/conversations/{conversation_id}/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_conversation(conversation_id: str):
    """
    Clear all messages in a conversation.

    Args:
        conversation_id: The conversation ID to clear
    """
    conversation = _conversations.get(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    conversation.messages.clear()
    conversation.updated_at = datetime.utcnow()
    logger.info(f"Cleared conversation {conversation_id}")
