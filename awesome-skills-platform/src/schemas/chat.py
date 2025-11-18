"""
Pydantic schemas for Chat/Conversation resources.
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class ChatMessage(BaseModel):
    """Schema for a chat message."""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)
    thinking: Optional[List[str]] = None
    timestamp: Optional[datetime] = None

    class Config:
        populate_by_name = True


class ChatRequest(BaseModel):
    """Schema for chat request."""
    agent_id: str = Field(..., alias="agentId", min_length=1)
    message: str = Field(..., min_length=1, max_length=50000)
    conversation_id: Optional[str] = Field(None, alias="conversationId")

    class Config:
        populate_by_name = True


class ChatResponse(BaseModel):
    """Schema for chat response."""
    agent_id: str = Field(..., alias="agentId")
    conversation_id: str = Field(..., alias="conversationId")
    message: str
    thinking: Optional[List[str]] = None
    model_id: str = Field(..., alias="modelId")
    stop_reason: Optional[str] = Field(None, alias="stopReason")
    timestamp: datetime

    class Config:
        populate_by_name = True


class Conversation(BaseModel):
    """Schema for a conversation."""
    id: str
    agent_id: str = Field(..., alias="agentId")
    title: Optional[str] = None
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True
