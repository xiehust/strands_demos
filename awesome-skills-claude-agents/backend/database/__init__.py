"""Database layer for Agent Platform.

This module provides a database abstraction layer using DynamoDB.

Usage:
    from database import db

    agents = await db.agents.list()
    agent = await db.agents.get("agent-id")
"""
from database.base import BaseDatabase, BaseTable
from database.dynamodb import DynamoDBDatabase

_db_instance = DynamoDBDatabase()


def get_database() -> BaseDatabase:
    """Get the database instance.

    Returns:
        BaseDatabase: DynamoDBDatabase instance.
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
