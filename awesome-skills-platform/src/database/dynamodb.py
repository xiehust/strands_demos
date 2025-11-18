"""
DynamoDB client and operations.
"""
import boto3
from typing import Any
from datetime import datetime
import uuid
from decimal import Decimal
from botocore.exceptions import ClientError

from src.core.config import settings


def convert_to_dynamodb_format(data: dict[str, Any]) -> dict[str, Any]:
    """Convert Python types to DynamoDB-compatible types."""
    result = {}
    for key, value in data.items():
        if isinstance(value, float):
            result[key] = Decimal(str(value))
        elif isinstance(value, dict):
            result[key] = convert_to_dynamodb_format(value)
        elif isinstance(value, list):
            result[key] = [
                convert_to_dynamodb_format(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    return result


class DynamoDBClient:
    """DynamoDB client wrapper for common operations."""

    def __init__(self):
        """Initialize DynamoDB client."""
        dynamodb_kwargs = {"region_name": settings.aws_region}
        if settings.dynamodb_endpoint_url:
            dynamodb_kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

        self.dynamodb = boto3.resource("dynamodb", **dynamodb_kwargs)
        self.agents_table = self.dynamodb.Table(settings.agents_table_name)
        self.skills_table = self.dynamodb.Table(settings.skills_table_name)
        self.mcp_table = self.dynamodb.Table(settings.mcp_table_name)

    # Agent operations
    def create_agent(self, agent_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new agent."""
        agent_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        item = {
            "id": agent_id,
            "createdAt": timestamp,
            "updatedAt": timestamp,
            **convert_to_dynamodb_format(agent_data),
        }

        self.agents_table.put_item(Item=item)
        return item

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        """Get an agent by ID."""
        try:
            response = self.agents_table.get_item(Key={"id": agent_id})
            return response.get("Item")
        except ClientError:
            return None

    def list_agents(self) -> list[dict[str, Any]]:
        """List all agents."""
        response = self.agents_table.scan()
        return response.get("Items", [])

    def update_agent(self, agent_id: str, agent_data: dict[str, Any]) -> dict[str, Any] | None:
        """Update an agent."""
        timestamp = datetime.utcnow().isoformat()
        agent_data["updatedAt"] = timestamp

        # Convert to DynamoDB format
        agent_data = convert_to_dynamodb_format(agent_data)

        # Build update expression
        update_expr = "SET " + ", ".join([f"{k} = :{k}" for k in agent_data.keys()])
        expr_attr_values = {f":{k}": v for k, v in agent_data.items()}

        try:
            response = self.agents_table.update_item(
                Key={"id": agent_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_attr_values,
                ReturnValues="ALL_NEW",
            )
            return response.get("Attributes")
        except ClientError:
            return None

    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        try:
            self.agents_table.delete_item(Key={"id": agent_id})
            return True
        except ClientError:
            return False

    # Skill operations
    def create_skill(self, skill_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new skill."""
        skill_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        item = {
            "id": skill_id,
            "createdAt": timestamp,
            "createdBy": "system",  # TODO: Replace with actual user ID in Phase 3
            **convert_to_dynamodb_format(skill_data),
        }

        self.skills_table.put_item(Item=item)
        return item

    def get_skill(self, skill_id: str) -> dict[str, Any] | None:
        """Get a skill by ID."""
        try:
            response = self.skills_table.get_item(Key={"id": skill_id})
            return response.get("Item")
        except ClientError:
            return None

    def list_skills(self) -> list[dict[str, Any]]:
        """List all skills."""
        response = self.skills_table.scan()
        return response.get("Items", [])

    def delete_skill(self, skill_id: str) -> bool:
        """Delete a skill."""
        try:
            self.skills_table.delete_item(Key={"id": skill_id})
            return True
        except ClientError:
            return False

    # MCP Server operations
    def create_mcp_server(self, mcp_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new MCP server configuration."""
        mcp_id = str(uuid.uuid4())

        item = {
            "id": mcp_id,
            "status": "offline",  # Default status
            "agentCount": 0,
            **convert_to_dynamodb_format(mcp_data),
        }

        self.mcp_table.put_item(Item=item)
        return item

    def get_mcp_server(self, mcp_id: str) -> dict[str, Any] | None:
        """Get an MCP server by ID."""
        try:
            response = self.mcp_table.get_item(Key={"id": mcp_id})
            return response.get("Item")
        except ClientError:
            return None

    def list_mcp_servers(self) -> list[dict[str, Any]]:
        """List all MCP servers."""
        response = self.mcp_table.scan()
        return response.get("Items", [])

    def update_mcp_server(self, mcp_id: str, mcp_data: dict[str, Any]) -> dict[str, Any] | None:
        """Update an MCP server."""
        # Convert to DynamoDB format
        mcp_data = convert_to_dynamodb_format(mcp_data)

        # Build update expression
        update_expr = "SET " + ", ".join([f"{k} = :{k}" for k in mcp_data.keys()])
        expr_attr_values = {f":{k}": v for k, v in mcp_data.items()}

        try:
            response = self.mcp_table.update_item(
                Key={"id": mcp_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_attr_values,
                ReturnValues="ALL_NEW",
            )
            return response.get("Attributes")
        except ClientError:
            return None

    def delete_mcp_server(self, mcp_id: str) -> bool:
        """Delete an MCP server."""
        try:
            self.mcp_table.delete_item(Key={"id": mcp_id})
            return True
        except ClientError:
            return False


# Global database client instance
db_client = DynamoDBClient()
