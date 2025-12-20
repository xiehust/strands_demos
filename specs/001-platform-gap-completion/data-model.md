# Data Model: Platform Gap Completion

**Feature**: 001-platform-gap-completion
**Date**: 2025-12-19

## Entity Overview

This feature introduces new entities for error handling, authentication, and enhances existing entities with user ownership.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│      User       │────<│      Agent      │────<│     Skill       │
│  (NEW)          │     │  (enhanced)     │     │  (enhanced)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       │
┌─────────────────┐     ┌─────────────────┐            │
│   AuthToken     │     │    Session      │            │
│  (NEW)          │     │  (enhanced)     │            │
└─────────────────┘     └─────────────────┘            │
                                                       │
┌─────────────────┐     ┌─────────────────┐            │
│  ErrorResponse  │     │   MCPServer     │────────────┘
│  (NEW)          │     │  (enhanced)     │
└─────────────────┘     └─────────────────┘
```

## New Entities

### User

Represents an authenticated user of the platform.

| Field | Type | Constraints | Description |
| ----- | ---- | ----------- | ----------- |
| user_id | string | PK, UUID | Unique user identifier |
| email | string | Unique, required | User email address |
| password_hash | string | Required | Bcrypt hashed password |
| created_at | datetime | Required | Account creation timestamp |
| last_login | datetime | Optional | Last successful login |
| is_active | boolean | Default: true | Account status |

**DynamoDB Key Schema**:
- PK: `USER#{user_id}`
- SK: `METADATA`
- GSI1PK: `EMAIL#{email}` (for login lookup)

---

### AuthToken

Represents JWT token metadata (tokens themselves are stateless).

| Field | Type | Constraints | Description |
| ----- | ---- | ----------- | ----------- |
| token_id | string | PK, UUID | Token identifier (jti claim) |
| user_id | string | FK→User, required | Owner of the token |
| issued_at | datetime | Required | Token issue time |
| expires_at | datetime | Required | Token expiration time |
| is_revoked | boolean | Default: false | Manual revocation flag |

**Note**: Used for token revocation checking. Most validation is stateless via JWT signature.

---

### ErrorResponse

Standard error response format (not persisted, schema only).

| Field | Type | Constraints | Description |
| ----- | ---- | ----------- | ----------- |
| code | string | Required | Error code (e.g., `AGENT_NOT_FOUND`) |
| message | string | Required | User-friendly error message |
| detail | string | Optional | Technical detail for debugging |
| suggested_action | string | Optional | Actionable guidance for user |
| request_id | string | Optional | Request correlation ID for support |

**Error Codes Taxonomy**:
- `VALIDATION_*`: Input validation errors (400)
- `AUTH_*`: Authentication errors (401)
- `FORBIDDEN_*`: Authorization errors (403)
- `NOT_FOUND_*`: Resource not found (404)
- `CONFLICT_*`: State conflict (409)
- `RATE_LIMIT_*`: Rate limiting (429)
- `SERVER_*`: Internal errors (500)
- `SERVICE_*`: External service errors (503)

---

## Enhanced Entities

### Agent (Enhanced)

Added `user_id` for data isolation.

| Field | Type | Constraints | Description |
| ----- | ---- | ----------- | ----------- |
| ... | ... | ... | (existing fields unchanged) |
| user_id | string | FK→User, required | Owner of this agent |
| updated_at | datetime | Required | Last modification timestamp |

**DynamoDB Key Schema** (unchanged PK/SK, new GSI):
- GSI1PK: `USER#{user_id}`
- GSI1SK: `AGENT#{agent_id}`

---

### Skill (Enhanced)

Added `user_id` for data isolation.

| Field | Type | Constraints | Description |
| ----- | ---- | ----------- | ----------- |
| ... | ... | ... | (existing fields unchanged) |
| user_id | string | FK→User, required (except system skills) | Owner of this skill |
| is_system | boolean | Default: false | System-provided skill (no user_id) |

**DynamoDB Key Schema**:
- GSI1PK: `USER#{user_id}` (null for system skills)
- GSI1SK: `SKILL#{created_at}`

---

### MCPServer (Enhanced)

Added `user_id` for data isolation.

| Field | Type | Constraints | Description |
| ----- | ---- | ----------- | ----------- |
| ... | ... | ... | (existing fields unchanged) |
| user_id | string | FK→User, required | Owner of this MCP config |

**DynamoDB Key Schema**:
- GSI1PK: `USER#{user_id}`
- GSI1SK: `MCP#{server_id}`

---

### Session (Enhanced)

Added `user_id` for data isolation and persistence.

| Field | Type | Constraints | Description |
| ----- | ---- | ----------- | ----------- |
| session_id | string | PK, UUID | Session identifier |
| agent_id | string | FK→Agent, required | Agent used in session |
| user_id | string | FK→User, required | Owner of this session |
| created_at | datetime | Required | Session start time |
| last_accessed | datetime | Required | Last activity timestamp |
| message_count | integer | Default: 0 | Number of messages exchanged |

**DynamoDB Key Schema**:
- PK: `SESSION#{session_id}`
- SK: `METADATA`
- GSI1PK: `USER#{user_id}`
- GSI1SK: `SESSION#{created_at}`

---

## State Transitions

### User Account States

```
┌─────────┐     register      ┌─────────┐
│  None   │ ─────────────────>│ Active  │
└─────────┘                   └─────────┘
                                   │
                              deactivate
                                   │
                                   ▼
                              ┌─────────┐
                              │Inactive │
                              └─────────┘
```

### Session States

```
┌─────────┐     create       ┌─────────┐     activity    ┌─────────┐
│  None   │ ────────────────>│ Active  │ ──────────────> │ Active  │
└─────────┘                  └─────────┘                 └─────────┘
                                  │                           │
                             1hr timeout                   delete
                                  │                           │
                                  ▼                           ▼
                             ┌─────────┐                ┌─────────┐
                             │ Expired │                │ Deleted │
                             └─────────┘                └─────────┘
```

---

## Validation Rules

### User

- Email: Valid email format, max 255 chars
- Password: Min 8 chars, at least 1 uppercase, 1 lowercase, 1 digit

### Agent (with user isolation)

- Name: 1-255 chars, unique per user (not globally)
- user_id: Must match authenticated user

### ErrorResponse

- code: Uppercase with underscores, max 50 chars
- message: Max 500 chars
- detail: Max 2000 chars
- suggested_action: Max 200 chars

---

## Migration Notes

### From Mock DB to DynamoDB

1. **Data Export**: Export existing mock data to JSON
2. **Schema Creation**: Create DynamoDB tables with GSIs
3. **User Assignment**: Assign existing data to a default admin user
4. **Verification**: Run integration tests against DynamoDB

### Backward Compatibility

- Mock DB retained for local development (`MOCK_DB=true` env var)
- DynamoDB used in production (`MOCK_DB=false` or absent)
- Interface unchanged: `db_client.get_agent()` etc.
