# Configuration Guide

This document provides detailed information about configuring the AI Agent Platform.

## Environment Variables

All configuration is done through environment variables in the `backend/.env` file. Copy `backend/.env.example` to `backend/.env` and customize as needed.

### Required Configuration

#### ANTHROPIC_API_KEY
- **Required**: Yes
- **Description**: Your Anthropic API key for accessing Claude models
- **Example**: `ANTHROPIC_API_KEY=sk-ant-api03-...`
- **Where to get**: https://console.anthropic.com/settings/keys

### Claude API Configuration

#### ANTHROPIC_BASE_URL
- **Required**: No
- **Default**: Anthropic's default API endpoint
- **Description**: Custom API base URL for routing requests through proxies or custom endpoints
- **Use cases**:
  - Corporate proxy servers
  - API gateways
  - Custom authentication layers
  - Rate limiting proxies
- **Example**: `ANTHROPIC_BASE_URL=https://api-proxy.example.com`
- **Note**: Leave empty to use Anthropic's default endpoint

#### CLAUDE_CODE_USE_BEDROCK
- **Required**: No
- **Default**: `false`
- **Type**: Boolean (`true` or `false`)
- **Description**: Use AWS Bedrock instead of Anthropic's API
- **Use cases**:
  - Using AWS Bedrock for Claude models
  - Leveraging AWS credits or enterprise agreements
  - Regional compliance requirements
  - AWS-native deployments
- **Example**: `CLAUDE_CODE_USE_BEDROCK=true`
- **Prerequisites**:
  - AWS credentials configured (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
  - Bedrock access enabled in your AWS account
  - Claude models enabled in Bedrock

#### CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS
- **Required**: No
- **Default**: `false`
- **Type**: Boolean (`true` or `false`)
- **Description**: Disable experimental beta features in Claude Code
- **Use cases**:
  - Production environments requiring stability
  - Avoiding potential breaking changes
  - Compliance with enterprise policies
- **Example**: `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=true`
- **Note**: Beta features may change or be removed without notice

#### DEFAULT_MODEL
- **Required**: No
- **Default**: `claude-sonnet-4-5-20250929`
- **Description**: Default Claude model to use for agents
- **Available models**:
  - `claude-opus-4-5-20251101` - Most capable, highest cost
  - `claude-sonnet-4-5-20250929` - Balanced performance and cost (recommended)
  - `claude-haiku-4-20250514` - Fastest, lowest cost
- **Example**: `DEFAULT_MODEL=claude-opus-4-5-20251101`
- **Note**: Can be overridden per-agent in agent configuration

### Server Configuration

#### DEBUG
- **Required**: No
- **Default**: `true`
- **Type**: Boolean (`true` or `false`)
- **Description**: Enable debug mode with auto-reload and verbose logging
- **Example**: `DEBUG=false` (for production)

#### HOST
- **Required**: No
- **Default**: `0.0.0.0`
- **Description**: Host address for the backend server
- **Example**: `HOST=127.0.0.1` (localhost only)

#### PORT
- **Required**: No
- **Default**: `8000`
- **Type**: Integer
- **Description**: Port number for the backend server
- **Example**: `PORT=3000`

#### CORS_ORIGINS
- **Required**: No
- **Default**: `["http://localhost:5173", "http://localhost:3000"]`
- **Type**: JSON array
- **Description**: Allowed CORS origins for frontend access
- **Example**: `CORS_ORIGINS=["https://myapp.example.com"]`

### AWS Configuration (Optional)

These are only needed if using AWS services (DynamoDB, S3) in production:

#### AWS_REGION
- **Default**: `us-west-2`
- **Description**: AWS region for DynamoDB and S3
- **Example**: `AWS_REGION=us-east-1`

#### AWS_ACCESS_KEY_ID
- **Description**: AWS access key for API access
- **Example**: `AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE`

#### AWS_SECRET_ACCESS_KEY
- **Description**: AWS secret key for API access
- **Example**: `AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

### DynamoDB Configuration (Production)

#### DYNAMODB_ENDPOINT
- **Required**: No
- **Default**: None (uses AWS)
- **Description**: Custom DynamoDB endpoint (for local development)
- **Example**: `DYNAMODB_ENDPOINT=http://localhost:8000`

#### DYNAMODB_AGENTS_TABLE
- **Default**: `agents`
- **Description**: DynamoDB table name for agents

#### DYNAMODB_SKILLS_TABLE
- **Default**: `skills`
- **Description**: DynamoDB table name for skills

#### DYNAMODB_MCP_TABLE
- **Default**: `mcp_servers`
- **Description**: DynamoDB table name for MCP servers

### S3 Configuration (Production)

#### S3_BUCKET
- **Default**: `agent-platform-skills`
- **Description**: S3 bucket name for storing skill packages

### Agent Configuration

#### AGENT_WORKSPACE_DIR
- **Required**: No
- **Default**: `./workspace` (relative to project root)
- **Description**: Default working directory for agents
- **Example**: `AGENT_WORKSPACE_DIR=/var/app/workspace`
- **Note**: Can be overridden per-agent in agent configuration

## Configuration Examples

### Development (Local)

```env
# Required
ANTHROPIC_API_KEY=sk-ant-api03-...

# Server
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Use defaults for everything else
```

### Production (Anthropic API)

```env
# Required
ANTHROPIC_API_KEY=sk-ant-api03-...

# Server
DEBUG=false
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=["https://myapp.example.com"]

# Model
DEFAULT_MODEL=claude-sonnet-4-5-20250929

# Disable experimental features in production
CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=true

# AWS (for DynamoDB and S3)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
DYNAMODB_AGENTS_TABLE=production-agents
DYNAMODB_SKILLS_TABLE=production-skills
DYNAMODB_MCP_TABLE=production-mcp-servers
S3_BUCKET=production-agent-skills
```

### Production (AWS Bedrock)

```env
# Required (AWS credentials instead of Anthropic API key)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# Use Bedrock
CLAUDE_CODE_USE_BEDROCK=true

# Server
DEBUG=false
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=["https://myapp.example.com"]

# Model
DEFAULT_MODEL=claude-sonnet-4-5-20250929

# Disable experimental features
CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=true

# DynamoDB and S3
DYNAMODB_AGENTS_TABLE=production-agents
DYNAMODB_SKILLS_TABLE=production-skills
DYNAMODB_MCP_TABLE=production-mcp-servers
S3_BUCKET=production-agent-skills
```

### Using Custom Proxy

```env
# Required
ANTHROPIC_API_KEY=sk-ant-api03-...

# Custom endpoint
ANTHROPIC_BASE_URL=https://api-proxy.internal.company.com

# Server
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

## Configuration Validation

The backend will validate configuration on startup and provide helpful error messages for:
- Missing required variables
- Invalid values
- Incompatible combinations

To test your configuration:

```bash
cd backend
source .venv/bin/activate
python -c "from config import settings; print('Config OK')"
```

## Security Best Practices

1. **Never commit `.env` files** - They contain sensitive credentials
2. **Use environment-specific files** - `.env.development`, `.env.production`
3. **Rotate API keys regularly** - Especially if exposed
4. **Use AWS IAM roles** - Instead of access keys in production
5. **Limit CORS origins** - Only allow trusted domains
6. **Enable TLS/SSL** - Use HTTPS in production
7. **Set DEBUG=false** - In production environments

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
- Ensure `.env` file exists in `backend/` directory
- Check that `ANTHROPIC_API_KEY` is set with a valid key
- Restart the server after updating `.env`

### "Connection refused to Anthropic API"
- Check your internet connection
- Verify your API key is valid at https://console.anthropic.com
- If using `ANTHROPIC_BASE_URL`, verify the proxy is accessible

### "AWS credentials not found" (when using Bedrock)
- Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- Or configure AWS CLI: `aws configure`
- Ensure Bedrock is enabled in your AWS account

### CORS errors in browser
- Add your frontend URL to `CORS_ORIGINS` in `.env`
- Format: `CORS_ORIGINS=["http://localhost:5173", "https://myapp.com"]`
- Restart the backend after updating

## Environment Variable Priority

Configuration is loaded in this order (later overrides earlier):

1. Default values in `config.py`
2. `.env` file in `backend/` directory
3. System environment variables

## Updating Configuration

After updating `.env`:

```bash
# Restart services
./restart.sh

# Or manually restart backend
cd backend
# Kill the process and restart
python main.py
```

The backend will automatically reload configuration on restart (no need to rebuild).
