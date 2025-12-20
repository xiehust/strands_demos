"""
Simple Memory Manager for Conversation History

This module provides a simple in-memory conversation storage.
No external dependencies required - conversations are stored in memory.

Note: Conversations are lost when the server restarts.
For production, consider using DynamoDB or Redis for persistence.
"""

import logging
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ConversationMessage:
    """A single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConversationSession:
    """A conversation session with message history."""
    session_id: str
    agent_id: str
    actor_id: str
    messages: list[ConversationMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, content: str):
        """Add a message to the conversation."""
        self.messages.append(ConversationMessage(role=role, content=content))

    def get_history(self) -> list[dict]:
        """Get conversation history as list of dicts."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]

    def clear(self):
        """Clear conversation history."""
        self.messages.clear()


class MemoryManager:
    """
    Simple in-memory conversation storage.

    Stores conversations in a dictionary keyed by session_id.
    """

    def __init__(self):
        """Initialize the Memory Manager."""
        self._sessions: dict[str, ConversationSession] = {}
        self.enabled = True
        logger.info("Memory Manager initialized (in-memory storage)")

    def get_or_create_session(
        self,
        session_id: str,
        agent_id: str = "default",
        actor_id: str = "default-user",
    ) -> ConversationSession:
        """
        Get an existing session or create a new one.

        Args:
            session_id: Unique conversation/session identifier
            agent_id: Agent identifier
            actor_id: User/actor identifier

        Returns:
            ConversationSession instance
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationSession(
                session_id=session_id,
                agent_id=agent_id,
                actor_id=actor_id,
            )
            logger.info(f"Created new session: {session_id}")

        return self._sessions[session_id]

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get a session by ID, returns None if not found."""
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session. Returns True if deleted, False if not found."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def list_sessions(self, agent_id: Optional[str] = None) -> list[str]:
        """List all session IDs, optionally filtered by agent_id."""
        if agent_id:
            return [
                sid for sid, session in self._sessions.items()
                if session.agent_id == agent_id
            ]
        return list(self._sessions.keys())

    def is_enabled(self) -> bool:
        """Check if memory is enabled (always True for in-memory)."""
        return self.enabled


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """
    Get or create the global MemoryManager instance.

    Returns:
        MemoryManager singleton instance
    """
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


def reset_memory_manager():
    """Reset the global MemoryManager instance (mainly for testing)."""
    global _memory_manager
    _memory_manager = None
