"""In-memory mock database for development."""
from __future__ import annotations

from datetime import datetime
from typing import TypeVar, Generic, Optional
from uuid import uuid4

from config import settings
from database.base import BaseTable, BaseDatabase

T = TypeVar("T", bound=dict)


class MockTable(BaseTable[T], Generic[T]):
    """Mock table for in-memory storage implementing BaseTable interface."""

    def __init__(self, name: str):
        self.name = name
        self._data: dict[str, T] = {}

    async def put(self, item: T) -> T:
        """Insert or update an item."""
        if "id" not in item:
            item["id"] = str(uuid4())
        if "created_at" not in item:
            item["created_at"] = datetime.now().isoformat()
        item["updated_at"] = datetime.now().isoformat()
        self._data[item["id"]] = item
        return item

    async def get(self, item_id: str) -> Optional[T]:
        """Get an item by ID."""
        return self._data.get(item_id)

    async def list(self, user_id: Optional[str] = None) -> list[T]:
        """List all items, optionally filtered by user_id."""
        items = list(self._data.values())
        if user_id:
            items = [item for item in items if item.get("user_id") == user_id]
        return items

    async def delete(self, item_id: str) -> bool:
        """Delete an item by ID."""
        if item_id in self._data:
            del self._data[item_id]
            return True
        return False

    async def update(self, item_id: str, updates: dict) -> Optional[T]:
        """Update an item."""
        if item_id not in self._data:
            return None
        item = self._data[item_id]
        for key, value in updates.items():
            if value is not None:
                item[key] = value
        item["updated_at"] = datetime.now().isoformat()
        return item

    # Synchronous versions for backward compatibility
    def put_sync(self, item: T) -> T:
        """Synchronous version of put."""
        if "id" not in item:
            item["id"] = str(uuid4())
        if "created_at" not in item:
            item["created_at"] = datetime.now().isoformat()
        item["updated_at"] = datetime.now().isoformat()
        self._data[item["id"]] = item
        return item

    def get_sync(self, item_id: str) -> Optional[T]:
        """Synchronous version of get."""
        return self._data.get(item_id)

    def list_sync(self, user_id: Optional[str] = None) -> list[T]:
        """Synchronous version of list."""
        items = list(self._data.values())
        if user_id:
            items = [item for item in items if item.get("user_id") == user_id]
        return items

    def delete_sync(self, item_id: str) -> bool:
        """Synchronous version of delete."""
        if item_id in self._data:
            del self._data[item_id]
            return True
        return False

    def update_sync(self, item_id: str, updates: dict) -> Optional[T]:
        """Synchronous version of update."""
        if item_id not in self._data:
            return None
        item = self._data[item_id]
        for key, value in updates.items():
            if value is not None:
                item[key] = value
        item["updated_at"] = datetime.now().isoformat()
        return item


class MockDatabase(BaseDatabase):
    """Mock database with multiple tables implementing BaseDatabase interface."""

    def __init__(self):
        self._agents = MockTable[dict]("agents")
        self._skills = MockTable[dict]("skills")
        self._mcp_servers = MockTable[dict]("mcp_servers")
        self._sessions = MockTable[dict]("sessions")
        self._users = MockTable[dict]("users")
        self._init_sample_data()

    @property
    def agents(self) -> MockTable:
        return self._agents

    @property
    def skills(self) -> MockTable:
        return self._skills

    @property
    def mcp_servers(self) -> MockTable:
        return self._mcp_servers

    @property
    def sessions(self) -> MockTable:
        return self._sessions

    @property
    def users(self) -> MockTable:
        return self._users

    async def health_check(self) -> bool:
        """Mock database is always healthy."""
        return True

    def _init_sample_data(self):
        """Initialize with sample data for demo."""
        # Sample agents
        self._agents.put_sync({
            "id": "agent-1",
            "name": "Customer Service Bot",
            "description": "Handles customer inquiries and support tickets",
            "model": "GPT-4o",
            "permission_mode": "default",
            "max_turns": 4096,
            "system_prompt": "You are a helpful customer service agent.",
            "allowed_tools": ["Read", "Write"],
            "skill_ids": ["skill-1", "skill-3"],
            "mcp_ids": ["mcp-2"],
            "working_directory": None,
            "enable_bash_tool": False,
            "enable_file_tools": True,
            "enable_web_tools": False,
            "enable_tool_logging": True,
            "enable_safety_checks": True,
            "status": "active",
        })

        self._agents.put_sync({
            "id": "agent-2",
            "name": "Data Analysis Agent",
            "description": "Analyzes data and generates reports",
            "model": "Claude 3 Opus",
            "permission_mode": "acceptEdits",
            "max_turns": 8192,
            "system_prompt": "You are a data analysis expert.",
            "allowed_tools": ["Read", "Write", "Bash"],
            "skill_ids": ["skill-2"],
            "mcp_ids": [],
            "working_directory": None,
            "enable_bash_tool": True,
            "enable_file_tools": True,
            "enable_web_tools": True,
            "enable_tool_logging": True,
            "enable_safety_checks": True,
            "status": "inactive",
        })

        self._agents.put_sync({
            "id": "agent-3",
            "name": "Content Generation Agent",
            "description": "Creates and edits content",
            "model": "GPT-4",
            "permission_mode": "default",
            "max_turns": 2048,
            "system_prompt": "You are a creative content writer.",
            "allowed_tools": ["Read", "Write"],
            "skill_ids": [],
            "mcp_ids": [],
            "working_directory": None,
            "enable_bash_tool": False,
            "enable_file_tools": True,
            "enable_web_tools": False,
            "enable_tool_logging": True,
            "enable_safety_checks": True,
            "status": "active",
        })

        # Default agent
        self._agents.put_sync({
            "id": "default",
            "name": "Default Agent",
            "description": "Default AI assistant",
            "model": "claude-sonnet-4-20250514",
            "permission_mode": "default",
            "max_turns": 4096,
            "system_prompt": "You are a helpful AI assistant.",
            "allowed_tools": ["Read", "Write", "Bash"],
            "skill_ids": [],
            "mcp_ids": [],
            "working_directory": None,
            "enable_bash_tool": True,
            "enable_file_tools": True,
            "enable_web_tools": False,
            "enable_tool_logging": True,
            "enable_safety_checks": True,
            "status": "active",
        })

        # Sample skills
        self._skills.put_sync({
            "id": "skill-1",
            "name": "QueryDatabase",
            "description": "Executes SQL queries on the customer database.",
            "created_by": "system",
            "version": "1.0.0",
            "is_system": True,
        })

        self._skills.put_sync({
            "id": "skill-2",
            "name": "SendEmail",
            "description": "Sends an email to a specified recipient.",
            "created_by": "user",
            "version": "1.0.0",
            "is_system": False,
        })

        self._skills.put_sync({
            "id": "skill-3",
            "name": "GenerateReport",
            "description": "Creates a PDF report from a data source.",
            "created_by": "user",
            "version": "1.1.0",
            "is_system": False,
        })

        # Sample MCP servers
        self._mcp_servers.put_sync({
            "id": "mcp-1",
            "name": "Production-Cluster-A",
            "description": "Main production cluster",
            "connection_type": "stdio",
            "config": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", settings.agent_workspace_dir],
            },
            "status": "online",
            "endpoint": "192.168.1.100:8080",
            "version": "v2.1.3",
            "agent_count": 150,
        })

        self._mcp_servers.put_sync({
            "id": "mcp-2",
            "name": "Staging-EU-West",
            "description": "Staging environment for EU region",
            "connection_type": "sse",
            "config": {"url": "http://staging-eu.internal:8080/sse"},
            "status": "offline",
            "endpoint": "10.0.5.23:8080",
            "version": "v2.1.1",
            "agent_count": 75,
        })

        self._mcp_servers.put_sync({
            "id": "mcp-3",
            "name": "Development-US-East",
            "description": "Development environment",
            "connection_type": "http",
            "config": {"url": "http://dev.mcp.internal:9000"},
            "status": "error",
            "endpoint": "dev.mcp.internal:9000",
            "version": "v2.2.0-beta",
            "agent_count": 12,
        })


# Global database instance
db = MockDatabase()
