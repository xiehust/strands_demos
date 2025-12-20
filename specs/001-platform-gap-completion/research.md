# Research: Platform Gap Completion

**Feature**: 001-platform-gap-completion
**Date**: 2025-12-19

## Research Topics

### 1. FastAPI Error Handling Best Practices

**Decision**: Use custom exception handlers with structured ErrorResponse model

**Rationale**:
- FastAPI's `@app.exception_handler` provides centralized error handling
- Pydantic models ensure consistent error response structure
- HTTPException subclasses allow domain-specific error types
- Aligns with Constitution Principle IV (Separation of Concerns)

**Alternatives Considered**:
- Middleware-based error handling: Rejected - less granular control
- Per-route try/catch: Rejected - code duplication, inconsistent responses

**Implementation Pattern**:
```python
class ErrorResponse(BaseModel):
    code: str  # e.g., "AGENT_NOT_FOUND"
    message: str  # User-friendly message
    detail: Optional[str] = None  # Technical detail for debugging
    suggested_action: Optional[str] = None  # e.g., "Please try again"

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.detail.get("code", "UNKNOWN_ERROR"),
            message=exc.detail.get("message", str(exc.detail)),
            suggested_action=exc.detail.get("suggested_action")
        ).model_dump()
    )
```

---

### 2. React Loading State Patterns

**Decision**: Use TanStack Query's built-in loading states + custom `useLoadingState` hook for non-query operations

**Rationale**:
- TanStack Query already manages `isLoading`, `isFetching` for server state
- Custom hook needed for imperative operations (form submissions, SSE initiation)
- Skeleton loaders for initial page load; spinners for in-place updates
- Aligns with Constitution Principle II (Streaming & Real-Time feedback)

**Alternatives Considered**:
- Global loading state (Redux/Zustand): Rejected - over-engineering for this scope
- Per-component useState: Rejected - code duplication

**Implementation Pattern**:
```typescript
// For mutations/imperative actions
const useLoadingState = () => {
  const [state, setState] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const execute = async <T>(fn: () => Promise<T>): Promise<T> => {
    setState('loading');
    try {
      const result = await fn();
      setState('success');
      return result;
    } catch (e) {
      setState('error');
      throw e;
    }
  };
  return { state, execute, isLoading: state === 'loading' };
};
```

---

### 3. FastAPI + DynamoDB Integration

**Decision**: Use `aioboto3` for async DynamoDB access with connection pooling via `aiobotocore`

**Rationale**:
- FastAPI is async-first; blocking boto3 calls would degrade performance
- aioboto3 provides same API as boto3 but async
- Single-table design pattern for DynamoDB efficiency
- Aligns with Constitution Principle V (Simplicity - use standard AWS patterns)

**Alternatives Considered**:
- Synchronous boto3 with thread pool: Rejected - unnecessary complexity
- PynamoDB ORM: Rejected - additional dependency, learning curve
- Direct HTTP calls: Rejected - reinventing boto3

**Implementation Pattern**:
```python
from aioboto3 import Session
from contextlib import asynccontextmanager

class DynamoDBClient:
    def __init__(self):
        self._session = Session()

    @asynccontextmanager
    async def get_table(self, table_name: str):
        async with self._session.resource('dynamodb') as dynamodb:
            table = await dynamodb.Table(table_name)
            yield table

    async def get_agent(self, agent_id: str) -> Optional[dict]:
        async with self.get_table('agents') as table:
            response = await table.get_item(Key={'PK': f'AGENT#{agent_id}', 'SK': 'METADATA'})
            return response.get('Item')
```

---

### 4. JWT Authentication for FastAPI

**Decision**: Use `python-jose` for JWT encoding/decoding with FastAPI dependency injection

**Rationale**:
- python-jose is the standard for JWT in Python, well-maintained
- FastAPI's `Depends()` pattern enables clean auth middleware
- Token refresh handled client-side with interceptor
- Aligns with Constitution Principle III (Security by Design)

**Alternatives Considered**:
- AWS Cognito full integration: Rejected for MVP - can add later
- Session-based auth: Rejected - doesn't scale well for API-first architecture
- API keys only: Rejected - no user identity for data isolation

**Implementation Pattern**:
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, "email": payload.get("email")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

### 5. Rate Limiting for FastAPI

**Decision**: Use `slowapi` library with Redis backend (or in-memory for development)

**Rationale**:
- slowapi is FastAPI-native, built on limits library
- Supports multiple storage backends (memory, Redis)
- Per-user rate limiting via JWT user_id
- Aligns with FR-017 (rate limiting to prevent abuse)

**Alternatives Considered**:
- Custom middleware: Rejected - reinventing well-tested library
- API Gateway rate limiting only: Rejected - no per-user granularity without auth header parsing
- nginx rate limiting: Rejected - can't do per-user without custom config

**Implementation Pattern**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

def get_user_id(request: Request) -> str:
    # Extract from JWT if authenticated, else use IP
    auth = request.headers.get("Authorization")
    if auth:
        token = auth.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub", get_remote_address(request))
    return get_remote_address(request)

limiter = Limiter(key_func=get_user_id, default_limits=["100/minute"])
```

---

### 6. Testing Strategy

**Decision**:
- Backend: pytest + pytest-asyncio + httpx (async test client)
- Frontend: Vitest + React Testing Library
- E2E: Playwright

**Rationale**:
- pytest-asyncio handles FastAPI's async endpoints
- httpx provides async HTTP client for integration tests
- Vitest already configured in frontend (per spec assumptions)
- Playwright for cross-browser E2E testing
- Aligns with Constitution Quality Standards (integration tests over unit tests for API)

**Alternatives Considered**:
- unittest: Rejected - pytest has better async support and fixtures
- Jest for frontend: Rejected - Vitest already configured, faster
- Cypress for E2E: Rejected - Playwright has better Python integration

**Implementation Pattern**:
```python
# Backend integration test
@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_agent(client):
    response = await client.post("/api/agents", json={"name": "Test Agent"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test Agent"
```

---

## Summary of Decisions

| Topic | Decision | Key Library |
| ----- | -------- | ----------- |
| Error Handling | Custom exception handlers + ErrorResponse model | FastAPI built-in |
| Loading States | TanStack Query + custom useLoadingState hook | @tanstack/react-query |
| Database | Async DynamoDB with aioboto3 | aioboto3 |
| Authentication | JWT with python-jose | python-jose |
| Rate Limiting | slowapi with in-memory/Redis | slowapi |
| Testing | pytest-asyncio, Vitest, Playwright | pytest, vitest, playwright |

All decisions align with Constitution principles and spec requirements.
