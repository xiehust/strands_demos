"""Application configuration settings."""
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# Calculate project root directory (backend's parent directory)
_BACKEND_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BACKEND_DIR.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Agent Platform API"
    app_version: str = "4.0.0"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Database Mode
    mock_db: bool = True  # Use in-memory mock (true) or DynamoDB (false)

    # AWS
    aws_region: str = "us-west-2"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    # DynamoDB
    dynamodb_endpoint: str | None = None  # Local DynamoDB endpoint
    dynamodb_table_prefix: str = ""  # Prefix for table names (e.g., "dev_", "prod_")
    dynamodb_agents_table: str = "agents"
    dynamodb_skills_table: str = "skills"
    dynamodb_mcp_table: str = "mcp_servers"
    dynamodb_users_table: str = "users"
    dynamodb_sessions_table: str = "sessions"

    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Rate Limiting
    rate_limit_per_minute: int = 100

    # S3
    s3_bucket: str = "agent-platform-skills"

    # Claude Agent SDK / Anthropic API Configuration
    anthropic_api_key: str = ""
    anthropic_base_url: str | None = None  # Custom API endpoint (optional)
    default_model: str = "claude-sonnet-4-5-20250929"

    # Claude Code Configuration
    claude_code_use_bedrock: bool = False  # Use AWS Bedrock instead of Anthropic API
    claude_code_disable_experimental_betas: bool = False  # Disable experimental features

    # Agent workspace directory (default: ./workspace relative to project root)
    agent_workspace_dir: str = str(_PROJECT_ROOT / "workspace")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
