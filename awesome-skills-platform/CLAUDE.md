# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Awesome Skills Platform** is an AI agent platform powered by Strands Agents SDK and AWS Bedrock Claude models. The platform enables users to create customizable AI agents with dynamic skill loading and Model Context Protocol (MCP) server integration.

**Architecture**: Simplified - Agents run directly in FastAPI backend (no AgentCore Runtime dependency).

**Current Status**: Phase 5-8 Complete ✅ - 核心功能全部就绪 (Week 7)

**Archtecture Design**: [ARCHITECTURE.md](./ARCHITECTURE.md)

**DEVELOPMENT_PLAN Summary**: [DEVELOPMENT_PLAN](./DEVELOPMENT_PLAN.md)
- **Rule**: Always update the plan when sub task is completed.
- Phase 1 (✅ Complete): Frontend static pages with mock data
- Phase 2 (✅ Complete): FastAPI backend with Agent/Skill/MCP CRUD
- Phase 3 (✅ Complete): Frontend-backend integration with TanStack Query and Vite proxy
- Phase 4 (✅ Complete): Strands Agent integration - Basic async chat working
- Phase 5 (✅ Complete): Skill system - 15 skills fully integrated with agents (2025-11-18)
- Phase 6 (✅ Complete): MCP integration - 3 connection types, tool discovery (2025-11-18)
- Phase 7 (✅ Complete): In-memory conversation storage (simplified from AgentCore Memory)
- Phase 8 (✅ Complete): Real-time streaming chat with SSE - Frontend fully connected (2025-11-18)
- **Next Priority**: Phase 9 - AWS production deployment (optional)

## Core Technologies

### Frontend (`/frontend/`)
- **React 19** + **TypeScript** + **Vite**
- **Tailwind CSS v4** with `@theme` directive (NOT tailwind.config.js)
- **React Router v6** for client-side routing
- **TanStack Query** for API state management and caching
- **Axios** for HTTP requests with Vite proxy configuration
- **Design System**: Space Grotesk font, Material Symbols Outlined icons, dark theme (#101622)

### Backend (`/src/`)
- **FastAPI** - REST API framework with Pydantic validation
- **Strands Agents SDK** (`strands-agents>=1.13.0`) - Agents run directly in backend
- **Python 3.12-3.13** (configured in pyproject.toml)
- **In-memory conversation storage** - Simple session-based history
- **DynamoDB** for metadata storage (agents, skills, MCPs)
- **boto3** for AWS service integration

### Key AWS Services
- **Bedrock Models**: Claude Sonnet 4.5, Haiku, etc.
- **DynamoDB**: Metadata and configuration storage
- **S3**: Skill ZIP package storage (optional)

## Repository Structure

```
.
├── frontend/                    # React frontend application
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/         # Reusable UI components (Button, Layout, Sidebar)
│   │   │   ├── chat/           # Chat interface components
│   │   │   ├── agents/         # Agent management components
│   │   │   ├── skills/         # Skill management components
│   │   │   └── mcp/            # MCP management components
│   │   ├── pages/              # Page components (ChatPage, AgentsPage, SkillsPage, MCPPage)
│   │   ├── types/              # TypeScript type definitions
│   │   ├── mocks/              # Mock data service (Phase 1 only)
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API integration (Phase 3)
│   │   ├── App.tsx             # Root component with routing
│   │   └── index.css           # Tailwind v4 configuration with @theme
│   ├── postcss.config.js       # PostCSS configuration for Tailwind v4
│   ├── package.json            # Frontend dependencies
│   └── PROJECT_README.md       # Detailed frontend documentation
│
├── src/                        # Backend Python code
│   ├── api/                    # FastAPI application
│   │   ├── main.py             # FastAPI app and routes
│   │   └── schemas.py          # Pydantic models
│   ├── database/               # Database layer
│   │   └── dynamodb.py         # DynamoDB CRUD operations
│   ├── skill_tool.py           # Skill loading and tool generation (Phase 5)
│   ├── ask_user_tool.py        # User interaction tool (Phase 5)
│   ├── test_main_agent.py      # Agent testing script (Phase 4+)
│   └── skills/                 # Pre-built skills (xlsx, docx, pptx, etc.)
│
├── scripts/                    # Utility scripts
│   └── create_dynamodb_tables.py # DynamoDB table creation script
│
├── ui_design/                  # UI design references (4 main screens)
│   ├── agent对话主界面/          # Chat interface mockup
│   ├── agent定制管理/            # Agent management mockup
│   ├── skill管理/               # Skill management mockup
│   └── mcp管理/                 # MCP management mockup
│
├── ARCHITECTURE.md             # Complete system architecture (82KB)
├── DEVELOPMENT_PLAN.md         # 11-phase development roadmap
├── pyproject.toml              # Backend Python dependencies
└── CLAUDE.md                   # This file
```

## Essential Commands

### Frontend Development

```bash
# Navigate to frontend directory
cd frontend/

# Install dependencies
npm install

# Start development server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Type checking
tsc -b

# Linting
npm run lint

# Preview production build
npm run preview
```

### Backend Development

```bash
# Install backend dependencies
uv sync

# Create DynamoDB tables (local or AWS)
uv run python scripts/create_dynamodb_tables.py

# Start FastAPI server
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Run agent tests (Phase 4+)
python src/test_main_agent.py

# View API documentation
# Open http://localhost:8000/docs
```

## Critical Architecture Concepts

### 1. Tailwind CSS v4 Configuration

**IMPORTANT**: This project uses Tailwind CSS v4 which has a different configuration approach:

- ✅ **Use `@theme` directive** in `frontend/src/index.css`
- ❌ **DO NOT** use `tailwind.config.js` (deleted in Phase 1)
- ✅ **PostCSS plugin**: `@tailwindcss/postcss` in `postcss.config.js`

**Example from `index.css`:**
```css
@import "tailwindcss";

@theme {
  --color-primary: #2b6cee;
  --color-bg-dark: #101622;
  --color-bg-light: #f6f6f8;
  --color-text-muted: #9da6b9;
  --font-sans: "Space Grotesk", system-ui, sans-serif;
}
```

**Using custom colors in components:**
```tsx
<div className="bg-bg-dark text-white border-primary">
  {/* bg-bg-dark, text-white, border-primary work because of @theme */}
</div>
```

### 2. TypeScript Import Requirements

The project uses `verbatimModuleSyntax` enabled. **Always use `import type` for type-only imports:**

```typescript
// ✅ Correct
import type { ReactNode, ButtonHTMLAttributes } from 'react';
import { useState } from 'react'; // Runtime import

// ❌ Wrong (will cause TS1484 error)
import { ReactNode, ButtonHTMLAttributes } from 'react';
```

### 3. Skills System Architecture ✅ **100% Complete - Fully Integrated**

Skills are **dynamic tool packages** loaded at agent runtime:

- **Location**: `src/agentcore_runtime/skills/{skill_name}/`
- **Manifest**: Each skill has a `SKILL.md` with YAML frontmatter
- **Loading**: `skill_tool.py` (221 lines) scans directories and generates tool definitions
- **Storage**: Skill ZIPs stored in S3, synced to AgentCore Runtime `/tmp` ⚠️ **Enhancement feature (optional)**
- **Tool Generation**: Skills become callable tools via `generate_skill_tool()`

**Current Status (2025-11-18)**:
- ✅ skill_tool.py core implementation complete
- ✅ 15 skills with SKILL.md loaded (xlsx, docx, pptx, pdf, theme-factory, etc.)
- ✅ SkillToolInterceptor with 3 event hooks
- ✅ **FULLY integrated into agent_manager.py** - agents can use skills
- ✅ **End-to-end testing passed** - Agent successfully uses skills
- ⚠️ Skill ZIP upload/S3 storage not implemented (optional enhancement)

**Example Skill Structure:**
```
src/agentcore_runtime/skills/xlsx/
├── SKILL.md          # Skill manifest with YAML frontmatter
├── recalc.py         # Python utilities (optional)
└── ...
```

**Current Skill Invocation Flow** (fully working):
1. User enables skill in agent configuration (DynamoDB: agent.skillIds)
2. agent_manager.py loads enabled skills via skill_tool.py ✅ **WORKING**
3. `generate_skill_tool()` creates a tool with SKILL.md as context
4. Agent invokes skill like: `Skill(command="xlsx")`
5. SkillToolInterceptor hooks capture and inject SKILL.md content
6. Agent processes skill instructions and performs requested tasks

**Completed**: skill_tool.py fully integrated with agent_manager.py

### 4. Model Context Protocol (MCP) Integration ✅ **100% Complete - Fully Working**

MCP allows agents to connect to **external tool servers** and use their capabilities:

- **Location**: `src/core/mcp_manager.py` (215 lines)
- **Connection Types**: stdio, SSE (Server-Sent Events), HTTP (Streamable)
- **Lifecycle Management**: Managed approach - Agent handles MCP client sessions automatically
- **Tool Discovery**: Automatic via `list_tools_sync()`

**Current Status (2025-11-18)**:
- ✅ MCP Manager implemented with 3 connection types
- ✅ Fully integrated into agent_manager.py
- ✅ **End-to-end testing passed** - Calculator MCP server
- ✅ Agent successfully used MCP tools (multiply: 25 × 48 = 1,200)
- ⚠️ Tool filtering and auto health-check (optional enhancements)

**Example MCP Configuration** (DynamoDB):
```json
{
  "id": "mcp-calculator",
  "name": "Calculator Server",
  "connectionType": "http",
  "endpoint": "http://localhost:8000/mcp/",
  "config": {},
  "status": "online"
}
```

**Current MCP Integration Flow** (fully working):
1. User enables MCP server in agent configuration (DynamoDB: agent.mcpIds)
2. agent_manager.py loads MCP client via mcp_manager.py ✅ **WORKING**
3. `MCPClient` passed directly to Agent (managed lifecycle approach)
4. Agent automatically manages MCP client session lifecycle
5. Agent discovers available tools via `list_tools_sync()`
6. Agent invokes MCP tools during conversation
7. MCP server executes tool and returns result

**API Endpoints**:
- `POST /api/mcp/{mcp_id}/test` - Test connection and list tools
- `GET /api/mcp/{mcp_id}/tools` - List all available tools

**Completed**: MCP fully integrated with agents, tested with Calculator server

### 5. Agent Runtime (Simplified Architecture) ✅ **Complete**

**Current State**: Agents run directly in FastAPI backend (no AgentCore Runtime dependency)

**Implemented**:
- ✅ Strands Agent SDK integrated
- ✅ BedrockModel configured (Claude Sonnet 4.5)
- ✅ agent_manager.py with Agent lifecycle management
- ✅ POST /api/chat endpoint (async conversation)
- ✅ In-memory conversation storage
- ✅ Temperature, max_tokens, prompt caching support

**Agent Configuration (from DynamoDB):**
```typescript
interface Agent {
  id: string;
  name: string;
  modelId: string;              // e.g., "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
  temperature: number;
  maxTokens: number;
  systemPrompt?: string;
  skillIds: string[];           // Enabled skills
  mcpIds: string[];             // Connected MCP servers
  status: 'active' | 'inactive';
}
```

### 6. Conversation Memory (In-Memory Storage) ✅ **Complete**

**Current State**: Simple in-memory conversation storage (no external dependencies)

**Implemented**:
- ✅ Memory Manager (`src/core/memory_manager.py`)
- ✅ Session-based conversation tracking
- ✅ ConversationSession dataclass for message history
- ✅ Agent-Memory integration (agent_manager.py)

**How It Works**:
1. conversation_id from frontend maps to session_id in memory
2. Each session stores message history (user/assistant messages)
3. Messages persist within server lifetime
4. Server restart clears all conversations

**Note**: For production persistence, consider adding DynamoDB or Redis storage

### 7. Real-Time Streaming Chat ✅ **Complete (Phase 8)**

**Current State (2025-11-18)**: SSE-based streaming fully implemented

**Implemented**:
- ✅ Backend SSE endpoint (`POST /api/chat/stream`)
- ✅ Frontend streaming service (`services/chat.ts`)
- ✅ `useChat` hook for managing streaming state
- ✅ Real-time text accumulation with blinking cursor
- ✅ Thinking blocks visualization
- ✅ Cancel stream support (AbortController)
- ✅ Auto-scroll to bottom
- ✅ **User browser testing passed**

**Implementation Details**:
- Uses **Server-Sent Events (SSE)** instead of WebSocket
- Fetch API with ReadableStream for client-side streaming
- Event types: `start`, `text`, `thinking`, `tool_use`, `tool_result`, `done`, `error`
- Real-time message accumulation in `useChat` hook

**Not Implemented** (optional enhancements):
- ❌ Markdown rendering with syntax highlighting
- ❌ Code block copy buttons
- ❌ Message editing/regeneration

### 8. Data Management Strategy

**Current (Phase 3)**: Frontend uses real API calls with TanStack Query

**Implementation:**
- All Agent/Skill/MCP data stored in DynamoDB
- Frontend uses Axios + TanStack Query for API requests
- Vite proxy routes `/api/*` to backend (`http://localhost:8000`)
- Data caching with 5-minute staleTime
- Optimistic updates with query invalidation

**Note:** ChatPage now uses real-time SSE streaming (Phase 8 complete - 2025-11-18)

## Development Workflow

### Starting a New Feature

1. **Check current phase** in DEVELOPMENT_PLAN.md
2. **Review UI design** in `ui_design/` directory for visual reference
3. **Read ARCHITECTURE.md** sections relevant to the feature
4. **Frontend work**: Start in `frontend/src/components/` or `frontend/src/pages/`
5. **Backend work**: Start in `src/api/` for REST endpoints, update schemas in `src/api/schemas.py`
6. **Database work**: Add CRUD operations in `src/database/dynamodb.py`

### Common Development Patterns

#### Adding a New React Component

```typescript
// frontend/src/components/common/NewComponent.tsx
import type { ReactNode } from 'react';
import clsx from 'clsx';

interface NewComponentProps {
  children: ReactNode;
  variant?: 'primary' | 'secondary';
  className?: string;
}

export function NewComponent({
  children,
  variant = 'primary',
  className
}: NewComponentProps) {
  return (
    <div className={clsx(
      'base-classes',
      {
        'bg-primary text-white': variant === 'primary',
        'bg-gray-700 text-gray-200': variant === 'secondary',
      },
      className
    )}>
      {children}
    </div>
  );
}
```

#### Adding a New Page Route

```typescript
// frontend/src/pages/NewPage.tsx
export function NewPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Page Title</h1>
      {/* Page content */}
    </div>
  );
}

// frontend/src/App.tsx
import { NewPage } from './pages/NewPage';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/new" element={<NewPage />} />
          {/* ... */}
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
```

#### Adding API Integration

```typescript
// 1. Define service in frontend/src/services/
import { api } from '../lib/api';
import type { NewItem } from '../types';

export const newItemsApi = {
  list: async (): Promise<NewItem[]> => {
    const response = await api.get<NewItem[]>('/api/items');
    return response.data;
  },

  create: async (data: Partial<NewItem>): Promise<NewItem> => {
    const response = await api.post<NewItem>('/api/items', data);
    return response.data;
  },
};

// 2. Use in component with TanStack Query
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { newItemsApi } from '../services/items';

function ItemsPage() {
  const queryClient = useQueryClient();
  const { data: items, isLoading } = useQuery({
    queryKey: ['items'],
    queryFn: newItemsApi.list,
  });

  const createMutation = useMutation({
    mutationFn: newItemsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
    },
  });

  // ... component code
}
```

### Build and Error Resolution

**Always run build to catch errors:**
```bash
cd frontend/
npm run build
```

**Common Issues:**

1. **Tailwind Unknown Utility Class**: Check if custom colors are defined in `@theme` in `index.css`
2. **TypeScript TS1484 Error**: Use `import type` for type-only imports
3. **PostCSS Plugin Error**: Ensure `@tailwindcss/postcss` is installed and configured
4. **Module Resolution**: Check `tsconfig.json` path mappings and Vite config

## Key Design Decisions

### Why Frontend-First?

From DEVELOPMENT_PLAN.md:
> **Week 5: 用户可见：完整静态 UI** - 4 个页面、Mock 数据、完整交互

Benefits:
- ✅ Early user feedback on UI/UX
- ✅ Frontend and backend teams can work in parallel (Phase 1 & 2)
- ✅ Reduces integration risk by validating interfaces early
- ✅ Demonstrates value quickly (Week 5 vs Week 14)

### Why Strands Agents SDK?

- **Flexible Deployment**: Can run standalone or with AgentCore Runtime
- **MCP Support**: `MCPClient` for Model Context Protocol servers
- **Tool System**: Dynamic tool loading and invocation
- **Event Hooks**: `BeforeModelCallEvent`, `AfterToolCallEvent`, `MessageAddedEvent`
- **Bedrock Integration**: Native support for AWS Bedrock models

### Why DynamoDB?

- **Serverless**: No infrastructure management, auto-scaling
- **Performance**: Single-digit millisecond latency
- **Flexible Schema**: Supports agent configuration, skills metadata, MCP configs
- **GSI Support**: Efficient querying by user_id, status, etc.

## Testing Strategy

### Frontend Testing (Phase 10)

```bash
# Unit tests with Vitest (to be implemented)
npm run test

# Component tests (to be implemented)
npm run test:components

# E2E tests (to be implemented)
npm run test:e2e
```

### Backend Testing

```bash
# Current: Manual agent testing
python src/test_main_agent.py

# Future: pytest unit tests (Phase 10)
pytest src/tests/

# API integration tests (Phase 10)
pytest src/tests/integration/
```

## Debugging Tips

### Frontend Debugging

1. **Check browser console** for React errors and network requests
2. **Use React DevTools** to inspect component state and props
3. **Verify Tailwind classes** using browser DevTools (check if classes are applied)
4. **Check mock data** in `frontend/src/mocks/data.ts`

### Backend Debugging (Future)

1. **Check CloudWatch Logs** for AgentCore Runtime errors
2. **Use AWS X-Ray** for distributed tracing
3. **Validate DynamoDB queries** using AWS Console
4. **Test MCP connections** with health check endpoint

## Performance Considerations

### Frontend Optimization

- **Code Splitting**: Use React.lazy() for route-based splitting (Phase 3)
- **Virtual Scrolling**: For long message lists and tables (Phase 8)
- **Memoization**: Use React.memo() and useMemo() for expensive components
- **Image Optimization**: Use appropriate image formats and lazy loading

### Backend Optimization

- **Prompt Caching**: Bedrock caches prompts with `cache_prompt="default"` (90% token savings)
- **DynamoDB Optimization**: Use GSI for efficient queries, batch operations
- **S3 Transfer Acceleration**: For large skill ZIP uploads
- **WebSocket Backpressure**: Limit concurrent connections and message buffer size

## Security Best Practices

1. **Input Validation**: Use Pydantic schemas for all API inputs (Phase 2)
2. **Authentication**: JWT tokens for API and WebSocket auth (Phase 3)
3. **IAM Least Privilege**: Minimal permissions for Lambda/ECS roles
4. **Secrets Management**: Use AWS Secrets Manager for API keys
5. **CORS Configuration**: Restrict origins in production
6. **XSS Prevention**: Sanitize user inputs, use Content Security Policy

## Related Documentation

- **ARCHITECTURE.md**: Complete system architecture (82KB, 2500+ lines)
- **DEVELOPMENT_PLAN.md**: 11-phase development roadmap (26KB)
- **frontend/PROJECT_README.md**: Detailed frontend documentation
- **UI Design References**: `ui_design/` directory (4 screens)

## Development Phases

| Phase | Status | Deliverable |
|-------|--------|-------------|
| Phase 0 | ⏭️ Skipped | AWS infrastructure setup (using existing AWS env) |
| Phase 1 | ✅ Complete | Frontend static pages with mock data |
| Phase 2 | ✅ Complete | FastAPI backend with Agent/Skill/MCP CRUD + DynamoDB |
| Phase 3 | ✅ Complete | Frontend-backend integration with TanStack Query + Vite proxy |
| Phase 4 | ✅ Complete | Strands Agent integration - Basic async chat |
| Phase 5 | ✅ Complete | Skill system - 15 skills fully integrated (2025-11-18) |
| Phase 6 | ✅ Complete | MCP integration - 3 connection types, tool discovery (2025-11-18) |
| Phase 7 | ✅ Complete | In-memory conversation storage (simplified) |
| Phase 8 | ✅ Complete | SSE streaming chat - Real-time frontend integration (2025-11-18) |
| Phase 9 | Not Started | AWS deployment (ECS, ALB, S3) |
| Phase 10 | Not Started | Testing and optimization |
| Phase 11 | Not Started | Production launch |

**Current Milestone**: Week 7 - Phases 5-8 Complete - AI Agent Platform Ready!
- Frontend: http://localhost:5173/ (Full-featured chat interface with streaming)
- Backend: http://localhost:8000 (Skills, MCP integrated, agents run directly)
- API Docs: http://localhost:8000/docs
- **Architecture**: Simplified - no AgentCore Runtime dependency
- **Next Priority**:
  - Phase 9: AWS production deployment (optional - system is fully functional locally)

## Quick Reference

### Important File Paths

**Frontend:**
- Tailwind config: `frontend/src/index.css` (Tailwind v4 @theme)
- PostCSS config: `frontend/postcss.config.js`
- Type definitions: `frontend/src/types/index.ts`
- Routing: `frontend/src/App.tsx`
- API client: `frontend/src/lib/api.ts`
- Services: `frontend/src/services/agents.ts`, `skills.ts`, `mcp.ts`
- Vite config: `frontend/vite.config.ts` (proxy setup)

**Backend:**
- FastAPI app: `src/api/main.py`
- Pydantic schemas: `src/api/schemas.py`
- DynamoDB operations: `src/database/dynamodb.py`
- Table creation: `scripts/create_dynamodb_tables.py`
- Skills (Phase 5): `src/skills/*/SKILL.md`

### Environment Variables

**Backend (Current):**
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default  # Optional, for local development

# DynamoDB
DYNAMODB_TABLE_PREFIX=awesome-skills-platform  # Optional, defaults to this

# Optional
S3_SKILLS_BUCKET=agent-platform-skills  # For skill ZIP storage (optional)
JWT_SECRET=<secret>  # Authentication (future)
```

**Frontend (Current):**
```bash
# Uses Vite proxy - no need for explicit API URL
# All /api/* requests automatically proxied to http://localhost:8000

# Phase 8 Complete (2025-11-18)
# Uses SSE streaming via /api/chat/stream endpoint
# No additional environment variables needed
```

### Design System Reference

- **Primary Color**: `#2b6cee` (use class: `bg-primary`, `text-primary`, `border-primary`)
- **Dark Background**: `#101622` (use class: `bg-bg-dark`)
- **Light Background**: `#f6f6f8` (use class: `bg-bg-light`)
- **Muted Text**: `#9da6b9` (use class: `text-text-muted`)
- **Font**: Space Grotesk (use class: `font-sans` - default)
- **Icons**: Material Symbols Outlined (use class: `material-symbols-outlined`)

### Component Architecture

- **Layout Pattern**: Layout > Sidebar + Main > Page
- **Button Variants**: primary, secondary, ghost, danger
- **Page Structure**: Title + Toolbar + Table/List + Actions
- **Form Pattern**: Label + Input + Validation + Submit

## Additional Notes

- All UI designs must match the visual references in `ui_design/` directory
- Follow the Space Grotesk font and Material Symbols icon system
- Maintain dark theme (#101622) as primary theme
- Keep TypeScript strict mode enabled
- Use functional components with hooks (no class components)
- Prefer composition over inheritance
- Write self-documenting code with clear naming
