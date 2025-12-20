<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version Change: 0.0.0 → 1.0.0 (MAJOR - Initial ratification)

Modified Principles: N/A (initial version)

Added Sections:
- Core Principles (5 principles)
  - I. SDK-First Integration
  - II. Streaming & Real-Time
  - III. Security by Design
  - IV. Separation of Concerns
  - V. Simplicity & Pragmatism
- Quality Standards
- Development Workflow
- Governance

Removed Sections: N/A (initial version)

Templates Requiring Updates:
- .specify/templates/plan-template.md ✅ Compatible (Constitution Check section exists)
- .specify/templates/spec-template.md ✅ Compatible (Requirements section aligns)
- .specify/templates/tasks-template.md ✅ Compatible (Phased approach aligns)

Follow-up TODOs: None
================================================================================
-->

# AI Agent Platform Constitution

## Core Principles

### I. SDK-First Integration

All agent functionality MUST be implemented through the official Claude Agent SDK (`claude-agent-sdk`).

- Agent sessions MUST use `ClaudeSDKClient` with `ClaudeAgentOptions` for configuration
- Built-in tools (Bash, Read, Write, Edit, Glob, Grep, WebFetch) MUST NOT be reimplemented
- Custom tools MUST use the `@tool` decorator pattern
- MCP server configurations MUST follow SDK's `mcp_servers` dictionary format
- Hooks (PreToolUse, PostToolUse) MUST be used for security checks and logging, not custom middleware

**Rationale**: The Claude Agent SDK provides battle-tested, maintained functionality. Reimplementing SDK features creates maintenance burden and diverges from upstream improvements.

### II. Streaming & Real-Time

All user-facing AI interactions MUST use Server-Sent Events (SSE) for response streaming.

- Chat endpoints MUST stream responses via SSE (`/api/chat/stream`)
- SSE messages MUST follow the defined JSON format: `{type, content, model}` for messages, `{type: "result", ...}` for completion
- Frontend MUST handle streaming progressively (show content as it arrives, not after completion)
- Tool calls MUST be visualized in real-time with their inputs and outputs
- Session continuity MUST be maintained via `session_id` across conversation turns

**Rationale**: Streaming provides immediate feedback, improves perceived performance, and enables users to see and potentially interrupt long-running operations.

### III. Security by Design

Security controls MUST be enforced at the agent execution layer, not deferred to UI.

- Dangerous command blocking MUST be implemented via PreToolUse hooks
- Permission modes (`default`, `acceptEdits`, `plan`, `bypassPermissions`) MUST be respected from agent configuration
- Tool allowlists (`allowed_tools`) MUST be enforced—agents MUST NOT access tools not in their allowlist
- API keys and secrets MUST NOT be logged, returned in API responses, or exposed in SSE streams
- Working directories MUST be sandboxed per-agent configuration (`working_directory`)

**Rationale**: AI agents can execute arbitrary code. Security controls at the execution layer prevent circumvention through UI manipulation or direct API calls.

### IV. Separation of Concerns

The platform MUST maintain clear boundaries between frontend, backend, and agent execution.

- **Frontend**: UI rendering, user input collection, SSE consumption, state display only
- **Backend API**: Request validation, session management, agent configuration, SSE orchestration
- **Agent Layer**: Conversation execution, tool invocation, MCP communication
- **Database**: Configuration persistence, session storage (mock now, DynamoDB in production)

Entity ownership:
- Agents, Skills, MCP configs: Backend owns creation/update/delete; frontend displays
- Sessions: Backend creates; agent layer writes; frontend reads via API
- Tool execution: Agent layer exclusively; backend observes via hooks

**Rationale**: Clear boundaries enable independent testing, deployment, and evolution of each layer without cascading changes.

### V. Simplicity & Pragmatism

Features MUST solve immediate, validated needs—not hypothetical future requirements.

- YAGNI (You Aren't Gonna Need It): Do not add features "just in case"
- Start simple: Use mock database for development; production infrastructure (DynamoDB, S3) only when deploying
- Prefer composition over inheritance: Combine existing SDK features rather than creating complex hierarchies
- Avoid premature abstraction: Three similar implementations justify an abstraction; one does not
- Configuration over code: Agent behavior changes SHOULD be achievable via config, not code changes

**Rationale**: Over-engineering slows development, increases bugs, and makes onboarding harder. Real user needs, not imagined ones, should drive complexity.

## Quality Standards

Code changes MUST meet these quality gates before merge:

- **Type Safety**: TypeScript strict mode for frontend; Pydantic models for all API contracts
- **Error Handling**: API errors MUST return structured responses with `{error, detail}` format
- **Logging**: Backend operations MUST log at appropriate levels (INFO for operations, WARNING for recoverable errors, ERROR for failures)
- **Documentation**: Public API endpoints MUST have OpenAPI documentation; complex functions MUST have docstrings

Testing philosophy:
- Integration tests over unit tests for API endpoints (test the contract, not implementation)
- Frontend component tests for complex interactive behavior
- Manual testing acceptable for UI styling and visual elements

## Development Workflow

The following workflow MUST be followed for feature development:

1. **Specification**: Create feature spec using `/speckit.specify` defining user scenarios and requirements
2. **Planning**: Generate implementation plan using `/speckit.plan` with technical context
3. **Task Generation**: Break down into actionable tasks using `/speckit.tasks`
4. **Implementation**: Execute tasks in dependency order, committing after each logical group
5. **Validation**: Verify against spec acceptance criteria before marking complete

Branch naming: `[issue#]-[feature-slug]` (e.g., `42-add-mcp-testing`)

Commit messages: Imperative mood, present tense, reference issue if applicable (e.g., "Add MCP connection test endpoint (#42)")

## Governance

This constitution supersedes all ad-hoc practices. When conflicts arise, constitution principles take precedence.

**Amendment Process**:
1. Propose amendment with rationale in a spec document
2. Review impact on existing principles and templates
3. Version bump according to semantic versioning:
   - MAJOR: Principle removal or fundamental redefinition
   - MINOR: New principle addition or material expansion
   - PATCH: Clarifications and non-semantic refinements
4. Update all dependent templates to maintain consistency

**Compliance Review**:
- All PRs SHOULD reference which principles apply to the changes
- Code reviews MUST verify adherence to applicable principles
- Deviations MUST be documented with explicit justification in the PR description

**Version**: 1.0.0 | **Ratified**: 2025-12-19 | **Last Amended**: 2025-12-19
