"""
Unit tests for Memory Manager.
"""
import os
import pytest
from unittest.mock import patch, MagicMock


class TestMemoryManager:
    """Tests for MemoryManager class."""

    def test_init_without_memory_id(self):
        """Test initialization without AGENTCORE_MEMORY_ID."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove env var if exists
            os.environ.pop("AGENTCORE_MEMORY_ID", None)

            from src.core.memory_manager import MemoryManager

            manager = MemoryManager()
            assert manager.enabled is False
            assert manager.memory_id is None

    def test_init_with_memory_id(self):
        """Test initialization with AGENTCORE_MEMORY_ID."""
        with patch.dict(os.environ, {"AGENTCORE_MEMORY_ID": "test-memory-123"}):
            from src.core.memory_manager import MemoryManager

            manager = MemoryManager()
            assert manager.enabled is True
            assert manager.memory_id == "test-memory-123"

    def test_init_with_parameter(self):
        """Test initialization with memory_id parameter."""
        from src.core.memory_manager import MemoryManager

        manager = MemoryManager(memory_id="param-memory-456")
        assert manager.enabled is True
        assert manager.memory_id == "param-memory-456"

    def test_is_enabled(self):
        """Test is_enabled method."""
        from src.core.memory_manager import MemoryManager

        # Disabled
        manager_disabled = MemoryManager(memory_id=None)
        assert manager_disabled.is_enabled() is False

        # Enabled
        manager_enabled = MemoryManager(memory_id="test-memory")
        assert manager_enabled.is_enabled() is True

    def test_create_session_manager_disabled(self):
        """Test create_session_manager when memory is disabled."""
        from src.core.memory_manager import MemoryManager

        manager = MemoryManager(memory_id=None)
        result = manager.create_session_manager(session_id="session-1")
        assert result is None

    @patch("src.core.memory_manager.AgentCoreMemorySessionManager")
    @patch("src.core.memory_manager.AgentCoreMemoryConfig")
    def test_create_session_manager_enabled(
        self, mock_config_class, mock_session_manager_class
    ):
        """Test create_session_manager when memory is enabled."""
        from src.core.memory_manager import MemoryManager

        mock_session_manager = MagicMock()
        mock_session_manager_class.return_value = mock_session_manager

        manager = MemoryManager(memory_id="test-memory-id")
        result = manager.create_session_manager(
            session_id="session-123",
            actor_id="user-456"
        )

        # Verify config was created correctly
        mock_config_class.assert_called_once_with(
            memory_id="test-memory-id",
            session_id="session-123",
            actor_id="user-456",
        )

        # Verify session manager was created
        assert result == mock_session_manager

    @patch("src.core.memory_manager.AgentCoreMemorySessionManager")
    @patch("src.core.memory_manager.AgentCoreMemoryConfig")
    def test_create_session_manager_exception(
        self, mock_config_class, mock_session_manager_class
    ):
        """Test create_session_manager handles exceptions gracefully."""
        from src.core.memory_manager import MemoryManager

        mock_session_manager_class.side_effect = Exception("Connection failed")

        manager = MemoryManager(memory_id="test-memory-id")
        result = manager.create_session_manager(session_id="session-123")

        assert result is None


class TestGetMemoryManager:
    """Tests for get_memory_manager singleton function."""

    def test_returns_singleton(self):
        """Test that get_memory_manager returns the same instance."""
        from src.core.memory_manager import get_memory_manager, reset_memory_manager

        # Reset to ensure clean state
        reset_memory_manager()

        manager1 = get_memory_manager()
        manager2 = get_memory_manager()

        assert manager1 is manager2

    def test_reset_memory_manager(self):
        """Test that reset_memory_manager creates new instance."""
        from src.core.memory_manager import get_memory_manager, reset_memory_manager

        manager1 = get_memory_manager()
        reset_memory_manager()
        manager2 = get_memory_manager()

        assert manager1 is not manager2
