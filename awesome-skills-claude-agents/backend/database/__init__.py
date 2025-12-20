"""Database layer for Agent Platform.

This module provides a database abstraction layer that switches between:
- MockDatabase: In-memory storage for development (MOCK_DB=true)
- DynamoDBDatabase: AWS DynamoDB for production (MOCK_DB=false)

Usage:
    from database import db

    agents = await db.agents.list()
    agent = await db.agents.get("agent-id")
"""
from config import settings
from database.base import BaseDatabase, BaseTable

# Conditionally import the appropriate database implementation
if settings.mock_db:
    from database.mock_db import MockDatabase
    _db_instance = MockDatabase()
else:
    from database.dynamodb import DynamoDBDatabase
    _db_instance = DynamoDBDatabase()


def get_database() -> BaseDatabase:
    """Get the database instance based on configuration.

    Returns:
        BaseDatabase: MockDatabase if MOCK_DB=true, DynamoDBDatabase otherwise.
    """
    return _db_instance


# Convenience alias for direct access
db = _db_instance

__all__ = [
    "BaseDatabase",
    "BaseTable",
    "get_database",
    "db",
]
