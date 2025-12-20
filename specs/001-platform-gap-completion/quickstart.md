# Quickstart: Platform Gap Completion

**Feature**: 001-platform-gap-completion
**Date**: 2025-12-19

This guide walks through testing the new functionality added by this feature.

## Prerequisites

- Node.js 18+ and npm
- Python 3.12+
- AWS credentials configured (for DynamoDB)
- Docker (optional, for local DynamoDB)

## Setup

### 1. Start Local DynamoDB (Development)

```bash
# Option A: Use Docker
docker run -d -p 8000:8000 amazon/dynamodb-local

# Option B: Use AWS DynamoDB (requires credentials)
export AWS_REGION=us-east-1
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies (including new ones)
uv pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env:
#   ANTHROPIC_API_KEY=your-key
#   JWT_SECRET_KEY=your-secret-key
#   DYNAMODB_TABLE_PREFIX=dev_
#   MOCK_DB=false  # Set to true for mock database

# Run server
python main.py
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## Testing New Features

### Test 1: Error Handling (P1)

**Verify structured error responses**:

```bash
# Test validation error (empty agent name)
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"name": ""}'

# Expected response (400):
{
  "code": "VALIDATION_FAILED",
  "message": "Invalid input data",
  "detail": "name: ensure this value has at least 1 characters",
  "suggested_action": "Please check your input and try again"
}
```

**Verify service unavailable error**:

```bash
# Stop DynamoDB, then make request
curl http://localhost:8000/api/agents \
  -H "Authorization: Bearer <token>"

# Expected response (503):
{
  "code": "SERVICE_UNAVAILABLE",
  "message": "Service temporarily unavailable. Please try again later.",
  "suggested_action": "Please wait a moment and retry"
}
```

### Test 2: Loading States (P2)

**Frontend verification**:

1. Open browser to http://localhost:5173
2. Navigate to Agents page
3. Verify skeleton loader appears during initial load
4. Click "Create Agent", fill form, click "Save"
5. Verify button shows spinner and form is disabled during save
6. Navigate to Chat, send message
7. Verify send button is disabled during streaming

### Test 3: Authentication (P5)

**Register and login**:

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePass123"}'

# Expected response (201):
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "user_id": "...",
    "email": "test@example.com"
  }
}

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePass123"}'
```

**Verify data isolation**:

```bash
# User A creates agent
curl -X POST http://localhost:8000/api/agents \
  -H "Authorization: Bearer <user_a_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Agent A"}'

# User B cannot see User A's agent
curl http://localhost:8000/api/agents \
  -H "Authorization: Bearer <user_b_token>"
# Should NOT include "Agent A"
```

### Test 4: Rate Limiting (FR-017)

```bash
# Send 101 requests quickly
for i in {1..101}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    http://localhost:8000/api/agents \
    -H "Authorization: Bearer <token>"
done

# 101st request should return 429:
{
  "code": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Please slow down.",
  "retry_after": 60
}
```

### Test 5: Data Persistence (P4)

```bash
# Create agent
curl -X POST http://localhost:8000/api/agents \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Persistent Agent"}'

# Note the agent_id in response

# Restart backend
pkill -f "python main.py"
python main.py

# Verify agent still exists
curl http://localhost:8000/api/agents/<agent_id> \
  -H "Authorization: Bearer <token>"
# Should return the agent
```

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Run specific test file
npm run test -- src/__tests__/components/ErrorBoundary.test.tsx
```

### E2E Tests

```bash
# From project root
cd e2e

# Install Playwright
npm install
npx playwright install

# Run E2E tests
npx playwright test

# Run with UI
npx playwright test --ui
```

## Troubleshooting

### "Service unavailable" error

- Check DynamoDB is running: `docker ps` or AWS console
- Verify `MOCK_DB=false` in .env if using DynamoDB
- Check AWS credentials: `aws sts get-caller-identity`

### "401 Unauthorized" error

- Token may be expired (15 min default)
- Use `/api/auth/refresh` to get new token
- Check JWT_SECRET_KEY matches between requests

### Tests failing

- Ensure test database is isolated: `DYNAMODB_TABLE_PREFIX=test_`
- Clear test data between runs
- Check pytest-asyncio is installed for async tests

## Environment Variables Reference

| Variable | Default | Description |
| -------- | ------- | ----------- |
| MOCK_DB | true | Use in-memory mock (true) or DynamoDB (false) |
| JWT_SECRET_KEY | - | Secret for JWT signing (required) |
| JWT_ALGORITHM | HS256 | JWT algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | 15 | Access token lifetime |
| REFRESH_TOKEN_EXPIRE_DAYS | 7 | Refresh token lifetime |
| DYNAMODB_TABLE_PREFIX | - | Prefix for DynamoDB tables |
| RATE_LIMIT_PER_MINUTE | 100 | Requests per minute per user |
