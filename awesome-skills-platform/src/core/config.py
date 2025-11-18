"""
Application configuration using pydantic-settings.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    app_name: str = "Agent Platform API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"

    # CORS Settings
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # DynamoDB Settings
    aws_region: str = "us-east-1"
    dynamodb_endpoint_url: str | None = None  # For local development
    agents_table_name: str = "agent-platform-agents"
    skills_table_name: str = "agent-platform-skills"
    mcp_table_name: str = "agent-platform-mcp-servers"

    # Development
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
