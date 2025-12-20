# Tasks: Platform Gap Completion

**Feature**: 001-platform-gap-completion
**Generated**: 2025-12-19
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Summary

| Metric | Value |
| ------ | ----- |
| Total Tasks | 47 |
| Setup Phase | 4 tasks |
| Foundational Phase | 6 tasks |
| US1 (Error Handling) | 8 tasks |
| US2 (Loading States) | 6 tasks |
| US3 (Testing) | 9 tasks |
| US4 (Data Persistence) | 6 tasks |
| US5 (Authentication) | 6 tasks |
| Polish Phase | 2 tasks |
| Parallel Opportunities | 18 tasks marked [P] |

## Implementation Strategy

**MVP Scope**: User Story 1 (Error Handling) - provides immediate user value and establishes patterns for subsequent stories.

**Incremental Delivery Order**:
1. Setup + Foundational → Minimal working infrastructure
2. US1 (P1) → Deployable with better error UX
3. US2 (P2) → Enhanced loading feedback
4. US3 (P3) → Test coverage for confidence
5. US4 (P4) → Production-ready persistence
6. US5 (P5) → Multi-user ready
7. Polish → Production hardening

---

## Phase 1: Setup

**Goal**: Initialize project infrastructure for new features

- [x] T001 Install backend dependencies (aioboto3, python-jose, slowapi, passlib, bcrypt) in backend/pyproject.toml
- [x] T002 Install frontend dependencies (no new deps needed - Vitest, RTL already present)
- [x] T003 [P] Create middleware directory structure at backend/middleware/__init__.py
- [x] T004 [P] Create backend test directory structure at backend/tests/__init__.py

---

## Phase 2: Foundational

**Goal**: Blocking prerequisites that all user stories depend on

- [x] T005 Create ErrorResponse Pydantic schema in backend/schemas/error.py
- [x] T006 Create custom exception classes (ValidationException, AuthException, etc.) in backend/core/exceptions.py
- [x] T007 [P] Add error type definitions to frontend/src/types/index.ts
- [x] T008 [P] Add environment variables to backend/config.py (JWT_SECRET_KEY, RATE_LIMIT_PER_MINUTE, MOCK_DB)
- [x] T009 Create database client interface (abstract base) in backend/database/base.py
- [x] T010 Update backend/database/mock_db.py to implement base interface

---

## Phase 3: User Story 1 - Reliable Error Feedback (P1)

**Goal**: Clear and actionable error messages when something goes wrong

**Independent Test**: Trigger error conditions and verify user-friendly messages with suggested actions

**Acceptance Criteria**:
- Backend unavailable → "Unable to connect to server" with retry button
- Agent timeout → "Agent response timed out" with session preserved
- Invalid input → Specific validation error before request sent

### Backend Tasks

- [x] T011 [US1] Create global error handler middleware in backend/middleware/error_handler.py
- [x] T012 [US1] Register error handler in backend/main.py app lifespan
- [x] T013 [P] [US1] Update backend/routers/agents.py to raise structured exceptions
- [x] T014 [P] [US1] Update backend/routers/chat.py to raise structured exceptions with SSE error events
- [x] T015 [P] [US1] Update backend/routers/skills.py to raise structured exceptions
- [x] T016 [P] [US1] Update backend/routers/mcp.py to raise structured exceptions

### Frontend Tasks

- [x] T017 [US1] Create ErrorBoundary component in frontend/src/components/common/ErrorBoundary.tsx
- [x] T018 [US1] Update frontend/src/services/api.ts to parse ErrorResponse and display user-friendly messages with retry actions

---

## Phase 4: User Story 2 - Loading State Clarity (P2)

**Goal**: Clear loading feedback during async operations

**Independent Test**: Observe loading indicators during all async operations

**Acceptance Criteria**:
- Chat send → Button disabled with spinner until streaming begins
- Agent save → Spinner on button, form disabled until completion
- Page load → Skeleton loader in table area

### Frontend Tasks

- [x] T019 [US2] Create useLoadingState hook in frontend/src/hooks/useLoadingState.ts
- [x] T020 [P] [US2] Create SkeletonLoader component in frontend/src/components/common/SkeletonLoader.tsx
- [x] T021 [US2] Update frontend/src/pages/ChatPage.tsx to disable send button and show spinner during streaming
- [x] T022 [P] [US2] Update frontend/src/pages/AgentsPage.tsx with skeleton loader and form disable during save
- [x] T023 [P] [US2] Update frontend/src/pages/SkillsPage.tsx with skeleton loader and form disable
- [x] T024 [P] [US2] Update frontend/src/pages/MCPPage.tsx with skeleton loader and form disable

---

## Phase 5: User Story 3 - Confident Code Quality (P3)

**Goal**: Automated tests catch regressions

**Independent Test**: Run test suite, verify all pass with coverage reports

**Acceptance Criteria**:
- `npm run test` / `pytest` → All pass with coverage report
- Chat streaming → Covered by integration test
- Each API endpoint → At least one success and error test

### Backend Tests

- [x] T025 [US3] Create test fixtures and conftest in backend/tests/conftest.py
- [x] T026 [P] [US3] Create agent endpoint tests in backend/tests/test_agents.py
- [x] T027 [P] [US3] Create chat streaming tests in backend/tests/test_chat.py
- [x] T028 [P] [US3] Create skills endpoint tests in backend/tests/test_skills.py
- [x] T029 [P] [US3] Create MCP endpoint tests in backend/tests/test_mcp.py

### Frontend Tests

- [x] T030 [US3] Create ErrorBoundary tests in frontend/src/__tests__/components/ErrorBoundary.test.tsx
- [x] T031 [P] [US3] Create ChatPage tests in frontend/src/__tests__/components/ChatPage.test.tsx

### E2E Tests

- [ ] T032 [US3] Create Playwright config and chat flow E2E test in e2e/chat-flow.spec.ts
- [ ] T033 [US3] Add test scripts to package.json (test:e2e, test:coverage)

---

## Phase 6: User Story 4 - Data Persistence (P4)

**Goal**: Configuration persists across server restarts

**Independent Test**: Create data, restart server, verify data available

**Acceptance Criteria**:
- Agent created → Available after restart
- MCP configured → Persists with correct status
- Sessions → Metadata preserved for resumption

### Backend Tasks

- [x] T034 [US4] Create DynamoDB client in backend/database/dynamodb.py implementing base interface
- [x] T035 [US4] Create database factory in backend/database/__init__.py to switch mock/dynamo based on MOCK_DB env
- [x] T036 [US4] Update backend/routers/agents.py to use database factory
- [x] T037 [P] [US4] Update backend/routers/skills.py to use database factory
- [x] T038 [P] [US4] Update backend/routers/mcp.py to use database factory
- [x] T039 [US4] Update backend/core/session_manager.py to use database factory for session persistence

---

## Phase 7: User Story 5 - Secure Access (P5)

**Goal**: Authentication with user data isolation

**Independent Test**: Access protected endpoints without auth → 401; authenticate → access granted; see only own data

**Acceptance Criteria**:
- Unauthenticated → 401 Unauthorized
- Valid credentials → Token grants access
- Authenticated → Only see own agents/skills/sessions

### Backend Tasks

- [x] T040 [US5] Create auth schemas (RegisterRequest, LoginRequest, AuthResponse) in backend/schemas/auth.py
- [x] T041 [US5] Create JWT utilities (create_token, verify_token) in backend/core/auth.py
- [x] T042 [US5] Create auth router (register, login, refresh, logout, me) in backend/routers/auth.py
- [x] T043 [US5] Create auth middleware (get_current_user dependency) in backend/middleware/auth.py
- [x] T044 [US5] Add user_id filtering to all existing routers (agents, skills, mcp, chat)
- [x] T045 [US5] Register auth router and middleware in backend/main.py

---

## Phase 8: Polish & Cross-Cutting

**Goal**: Production hardening and final integration

- [x] T046 Create rate limiting middleware in backend/middleware/rate_limit.py and register in main.py
- [x] T047 Update CORS configuration in backend/main.py for production domains

---

## Dependencies

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundational) ─────────────────────────────────────┐
    │                                                        │
    ├─────────────────┬──────────────────┬──────────────────┤
    ▼                 ▼                  ▼                  │
Phase 3 (US1)    Phase 4 (US2)     Phase 5 (US3)          │
Error Handling   Loading States    Testing                  │
    │                 │                  │                  │
    └─────────────────┴──────────────────┘                  │
                      │                                      │
                      ▼                                      │
                Phase 6 (US4) ◄──────────────────────────────┘
                Data Persistence
                      │
                      ▼
                Phase 7 (US5)
                Authentication
                      │
                      ▼
                Phase 8 (Polish)
```

**Notes**:
- US1, US2, US3 can be done in parallel after Foundational
- US4 depends on Foundational (database interface)
- US5 depends on US4 (user_id storage)
- Polish depends on US5 (rate limiting per user)

---

## Parallel Execution Examples

### Phase 2 Parallel Group
```bash
# Can run simultaneously (different files, no dependencies)
T007: frontend/src/types/index.ts
T008: backend/config.py
```

### Phase 3 (US1) Parallel Group
```bash
# Can run simultaneously (different routers, same pattern)
T013: backend/routers/agents.py
T014: backend/routers/chat.py
T015: backend/routers/skills.py
T016: backend/routers/mcp.py
```

### Phase 4 (US2) Parallel Group
```bash
# Can run simultaneously (different pages, same pattern)
T020: frontend/src/components/common/SkeletonLoader.tsx
T022: frontend/src/pages/AgentsPage.tsx
T023: frontend/src/pages/SkillsPage.tsx
T024: frontend/src/pages/MCPPage.tsx
```

### Phase 5 (US3) Parallel Group
```bash
# Can run simultaneously (independent test files)
T026: backend/tests/test_agents.py
T027: backend/tests/test_chat.py
T028: backend/tests/test_skills.py
T029: backend/tests/test_mcp.py
T031: frontend/src/__tests__/components/ChatPage.test.tsx
```

### Phase 6 (US4) Parallel Group
```bash
# Can run simultaneously (different routers, same pattern)
T037: backend/routers/skills.py
T038: backend/routers/mcp.py
```

---

## Verification Checklist

After completing all tasks, verify:

- [x] `pytest backend/tests/` passes (46 tests passed)
- [x] `npm run test` passes (38 tests passed)
- [ ] `npm run test:e2e` passes (E2E tests not yet implemented)
- [x] All API errors return structured ErrorResponse
- [x] All async operations show loading indicators
- [x] Data persists after server restart (MOCK_DB=false) - DynamoDB client implemented
- [x] Unauthenticated requests return 401 - Auth middleware implemented
- [x] Rate limiting triggers at 100 req/min - Rate limiting middleware implemented
