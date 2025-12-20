# Agent Platform Architecture Design Document

**Version:** 3.0 (Simplified)
**Last Updated:** December 2025
**Status:** Production-Ready Design (No AgentCore Runtime)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Architecture Layers](#3-architecture-layers)
4. [Core Components](#4-core-components)
5. [Data Models](#5-data-models)
6. [API Design](#6-api-design)
7. [Technology Stack](#7-technology-stack)
8. [Deployment Architecture](#8-deployment-architecture)
9. [Security & Best Practices](#9-security--best-practices)
10. [Performance & Scalability](#10-performance--scalability)
11. [Future Enhancements](#11-future-enhancements)

---

## 1. Executive Summary

The Agent Platform is a conversational AI system that enables users to interact with customizable AI agents powered by AWS Bedrock and Claude models. The platform uses the **Strands Agents SDK** to run agents directly in the FastAPI backend, with a simple in-memory conversation storage system. It provides a sophisticated skill and tool ecosystem through Skills and Model Context Protocol (MCP) servers.

### Architecture: Simplified

**Key Change**: Agents run directly in the FastAPI backend process - no AgentCore Runtime dependency. This simplifies deployment and reduces external dependencies.

### Key Capabilities

- **Agent Management**: Create and configure custom agents with different models, parameters, and capabilities
- **Direct Agent Execution**: Agents run directly in FastAPI backend using Strands SDK
- **In-Memory Storage**: Simple session-based conversation history (server-side memory)
- **Dynamic Skill System**: Extensible architecture supporting both pre-built and user-generated skills
- **MCP Integration**: First-class support for Model Context Protocol servers using Strands MCPClient
- **Real-time Streaming**: SSE-based streaming for responsive conversational experiences
- **Rich Media Support**: Handle text, images, markdown, code blocks, and structured tool outputs

### Design Principles

1. **Simplicity**: Run agents directly in backend without external runtime dependencies
2. **Modularity**: Clean separation between frontend, API, business logic, and data layers
3. **Extensibility**: Plugin-based architecture for Skills and MCP servers
4. **Observability**: Comprehensive logging and monitoring of agent interactions
5. **Security**: Input validation and proper authentication
6. **Performance**: Efficient streaming and multi-layer caching

---

## 2. System Overview

### 2.1 High-Level Architecture (Simplified)

```
┌─────────────────────────────────────────┐
│  React Frontend (Vite + Tailwind)       │
│  • Chat Interface • Agent Mgmt           │
│  • Skill Mgmt • MCP Mgmt                 │
└────────────────┬────────────────────────┘
                 │ HTTP/REST + SSE
┌────────────────▼────────────────────────┐
│  FastAPI Backend (uvicorn)               │
│  • REST endpoints • SSE streaming        │
│  • Strands Agent SDK (runs directly)     │
│  • BedrockModel • Skill Tools • MCP      │
│  • In-Memory Conversation Storage        │
└─────┬───────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│  AWS Services                            │
│  ┌─────────────┐   ┌──────────────────┐ │
│  │  DynamoDB   │   │  AWS Bedrock     │ │
│  │  • agents   │   │  • Claude Models │ │
│  │  • skills   │   │  (Sonnet, Haiku) │ │
│  │  • mcp_cfg  │   └──────────────────┘ │
│  └─────────────┘                         │
│  ┌─────────────┐                         │
│  │  S3 Bucket  │  (optional)             │
│  │  • Skills   │                         │
│  └─────────────┘                         │
└─────────────────────────────────────────┘
```

**Key Simplifications**:
- No AgentCore Runtime - agents run in FastAPI process
- No AgentCore Memory - simple in-memory session storage
- SSE instead of WebSocket for streaming

### 2.2 Data Flow Architecture (Simplified)

```
User Input (Text/Image)
        │
        ▼
┌───────────────────┐
│  Frontend         │  1. User selects agent
│  Validation       │  2. Sends message via HTTP POST
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  FastAPI          │  3. Validates input payload
│  Backend          │  4. Loads agent config from DynamoDB
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Agent Manager    │  5. Creates/retrieves Strands Agent
│  (in-process)     │  6. Loads enabled skills and MCP tools
│                   │  7. Gets conversation history from memory
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Strands Agent    │  8. Processes user message
│  (BedrockModel)   │  9. Invokes tools if needed
│                   │  10. Generates response via Claude
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Memory Manager   │  11. Stores user message in session
│  (in-memory)      │  12. Stores assistant response in session
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  SSE Streaming    │  13. Streams tokens back via SSE
│  Response         │  14. Includes tool use events
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Frontend         │  15. Renders streaming response
│  Display          │  16. Formats tool calls, code blocks
│                   │  17. Updates conversation UI
└───────────────────┘
```

---

## 3. Architecture Layers

### 3.1 Presentation Layer (Frontend)

**Technology**: React 18+ with Vite, TypeScript, Tailwind CSS

**Design System Reference**: `/home/ubuntu/workspace/strands_demos/awesome-skills-platform/ui_design/`

#### Design Specifications

The UI design follows a consistent design system with:

- **Typography**: Space Grotesk font family (weights: 300-700)
- **Color Palette**:
  - Primary: `#2b6cee` (blue for interactive elements)
  - Background Light: `#f6f6f8` (light mode)
  - Background Dark: `#101622` (dark mode)
  - Text: `#ffffff` (dark mode), `#101622` (light mode)
  - Muted: `#9da6b9` (secondary text)
- **Icons**: Material Symbols Outlined
- **Layout**: Sidebar navigation with main content area
- **Dark Mode**: Tailwind CSS dark mode with `dark:` prefix

#### Four Main UI Modules

**1. Agent对话主界面 (Main Chat Interface)**
   - Location: `/home/ubuntu/workspace/strands_demos/awesome-skills-platform/ui_design/agent对话主界面/`
   - Left sidebar: Chat history list with active conversation highlighting
   - Main area: Conversation view with message bubbles
   - Tool call display: Visual indicators for skill/MCP invocations
   - Input area: Text input with file attachment button
   - Skill/MCP toggles: Checkboxes to enable skills and MCP servers
   - "New Chat" button in sidebar

**2. Agent定制管理 (Agent Management)**
   - Location: `/home/ubuntu/workspace/strands_demos/awesome-skills-platform/ui_design/agent定制管理/`
   - Left panel: Table view with agent list (name, model, status)
   - Right panel: Configuration panel for editing agent settings
   - Configuration options:
     - Model selector dropdown
     - Max tokens slider
     - Thinking mode toggle
     - Thinking budget slider (when enabled)
     - Skills multi-select checkboxes
     - MCP servers multi-select checkboxes
   - "Create New Agent" button

**3. Skill管理 (Skill Management)**
   - Location: `/home/ubuntu/workspace/strands_demos/awesome-skills-platform/ui_design/skill管理/`
   - Top toolbar: Search bar and filter controls
   - Action buttons:
     - "Upload ZIP" button for skill package upload
     - "Create with Agent" button for AI-assisted skill generation
   - Skill table: Name, description, created date, actions
   - Actions per skill: Edit, Delete icons

**4. MCP管理 (MCP Management)**
   - Location: `/home/ubuntu/workspace/strands_demos/awesome-skills-platform/ui_design/mcp管理/`
   - Top toolbar: Search and filter controls
   - MCP table: Name, connection type, status, actions
   - Status indicators:
     - Online (green)
     - Offline (gray)
     - Error (red)
   - Actions: Add, Edit, Delete, Test Connection
   - Visual health monitoring

#### Component Architecture

```
src/
├── App.tsx                          # Root component with routing
├── main.tsx                         # Entry point
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx        # Main chat container
│   │   ├── MessageList.tsx          # Scrollable message display
│   │   ├── MessageItem.tsx          # Individual message rendering
│   │   ├── InputArea.tsx            # Text/image input controls
│   │   ├── ChatHistorySidebar.tsx   # Left sidebar with conversation list
│   │   ├── SkillMCPToggles.tsx      # Checkboxes for skills/MCP
│   │   └── StreamingIndicator.tsx   # Typing indicator
│   ├── agents/
│   │   ├── AgentTable.tsx           # Table view of agents
│   │   ├── AgentRow.tsx             # Individual agent row
│   │   ├── AgentConfigPanel.tsx     # Right-side configuration panel
│   │   ├── ModelSelector.tsx        # Bedrock model dropdown
│   │   ├── ThinkingToggle.tsx       # Thinking mode controls
│   │   └── ToolsSelector.tsx        # Multi-select for skills/MCPs
│   ├── skills/
│   │   ├── SkillTable.tsx           # Table view of skills
│   │   ├── SkillRow.tsx             # Individual skill row
│   │   ├── SkillToolbar.tsx         # Search and filter controls
│   │   ├── SkillUploadModal.tsx     # ZIP upload interface
│   │   └── SkillGeneratorModal.tsx  # AI-assisted skill creation
│   ├── mcp/
│   │   ├── MCPTable.tsx             # List of MCP configurations
│   │   ├── MCPRow.tsx               # Individual MCP row with status
│   │   ├── MCPToolbar.tsx           # Search and filter controls
│   │   ├── MCPForm.tsx              # Create/edit MCP form
│   │   └── MCPStatusIndicator.tsx   # Status badge component
│   └── common/
│       ├── Layout.tsx               # App shell with navigation
│       ├── Sidebar.tsx              # Navigation menu
│       ├── SearchBar.tsx            # Universal search component
│       └── LoadingSpinner.tsx       # Loading states
├── hooks/
│   ├── useWebSocket.ts              # WebSocket connection manager
│   ├── useStreamingChat.ts          # Chat streaming logic
│   ├── useAgentAPI.ts               # Agent CRUD operations
│   ├── useSkillAPI.ts               # Skill CRUD operations
│   └── useMCPAPI.ts                 # MCP CRUD operations
├── services/
│   ├── api.ts                       # Axios client configuration
│   ├── websocket.ts                 # WebSocket client wrapper
│   └── storage.ts                   # Local storage utilities
├── types/
│   ├── agent.types.ts               # Agent-related TypeScript types
│   ├── skill.types.ts               # Skill-related types
│   ├── message.types.ts             # Message/chat types
│   └── mcp.types.ts                 # MCP configuration types
└── utils/
    ├── formatters.ts                # Text formatting utilities
    ├── validators.ts                # Input validation
    └── markdown.ts                  # Markdown rendering helpers
```

#### State Management Strategy

**Global State**: TanStack Query (React Query) for server state
- Agent configurations cached and synced
- Skill metadata cached with automatic revalidation
- MCP server status cached and monitored

**Local State**: React hooks (`useState`, `useReducer`) for UI state
- Active conversation
- Input field state
- Modal visibility
- Selection states

**WebSocket State**: Custom `useWebSocket` hook
- Connection status
- Message queue
- Reconnection logic
- Heartbeat management

---

### 3.2 API Layer (Backend)

**Technology**: FastAPI + Uvicorn

#### API Structure

```python
# src/api/main.py
from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB, load skills, connect MCP servers
    await startup_event()
    yield
    # Shutdown: Close connections
    await shutdown_event()

app = FastAPI(title="Agent Platform API", version="2.0.0", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from routers import agents, skills, mcp, chat, memory
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["mcp"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}
```

#### Router Organization

```
src/api/
├── main.py                  # FastAPI app initialization
├── routers/
│   ├── agents.py            # Agent CRUD endpoints + deployment
│   ├── skills.py            # Skill CRUD endpoints
│   ├── mcp.py               # MCP CRUD endpoints
│   ├── chat.py              # Chat WebSocket endpoint
│   └── memory.py            # AgentCore Memory search endpoints
├── middleware/
│   ├── auth.py              # JWT authentication
│   ├── logging.py           # Request/response logging
│   └── error_handler.py     # Global exception handling
├── dependencies/
│   ├── auth.py              # Auth dependency injection
│   └── dynamodb.py          # DynamoDB session management
└── schemas/
    ├── agent.py             # Pydantic models for agents
    ├── skill.py             # Pydantic models for skills
    ├── mcp.py               # Pydantic models for MCP
    ├── message.py           # Pydantic models for messages
    └── memory.py            # Pydantic models for memory queries
```

---

### 3.3 Business Logic Layer

**Technology**: Strands Agents SDK + Custom Python Modules

#### Core Modules

```
src/core/
├── agent_manager.py         # Agent lifecycle management (runs agents directly)
├── skill_manager.py         # Skill loading and validation
├── mcp_manager.py           # MCP server connection handling (MCPClient)
├── memory_manager.py        # Simple in-memory conversation storage
└── streaming_handler.py     # SSE streaming coordinator
```

#### Agent Manager (Simplified - No AgentCore)

```python
# src/core/agent_manager.py
from strands import Agent
from strands.models import BedrockModel
from typing import Dict, Optional
import logging

from src.database.dynamodb import db_client
from src.skill_tool import generate_skill_tool, SkillToolInterceptor
from src.core.mcp_manager import mcp_manager
from src.core.memory_manager import get_memory_manager

class AgentManager:
    """Manages agent lifecycle - agents run directly in FastAPI backend"""

    def __init__(self):
        self._agents: dict[str, dict] = {}
        self._models: dict[str, dict] = {}
        self._skill_tool = None
        self._skill_interceptor = None

    def get_or_create_agent(
        self,
        agent_id: str,
        session_id: Optional[str] = None,
    ) -> Agent:
        """Get cached agent or create new one from DynamoDB config"""
        cache_key = f"{agent_id}:{session_id}" if session_id else agent_id

        if cache_key in self._agents:
            return self._agents[cache_key]["agent"]

        # Load config from DynamoDB
        agent_config = db_client.get_agent(agent_id)
        if not agent_config:
            raise ValueError(f"Agent {agent_id} not found")

        agent = self._create_agent_from_config(agent_config)
        model_id = agent_config.get("modelId")
        self._agents[cache_key] = {"agent": agent, "model_id": model_id}

        return agent

    def _create_agent_from_config(self, config: dict) -> Agent:
        """Create Strands Agent from configuration"""
        model_id = config.get("modelId")
        model, _ = self._get_or_create_model(model_id, config)

        system_prompt = config.get("systemPrompt")
        skill_ids = config.get("skillIds", [])
        mcp_ids = config.get("mcpIds", [])

        tools = []
        hooks = []

        # Load skills if enabled
        if skill_ids:
            skill_tool = self._get_or_create_skill_tool()
            if skill_tool:
                tools.append(skill_tool)
                if self._skill_interceptor:
                    hooks.append(self._skill_interceptor)

        # Load MCP clients if enabled
        for mcp_id in mcp_ids:
            mcp_client = mcp_manager.get_mcp_client(mcp_id)
            if mcp_client:
                tools.append(mcp_client)

        # Create agent (runs in-process, no AgentCore Runtime)
        agent = Agent(
            model=model,
            system_prompt=system_prompt or "You are a helpful AI assistant.",
            tools=tools if tools else None,
            hooks=hooks if hooks else None,
        )

        return agent

    def _get_or_create_model(self, model_id: str, config: dict) -> tuple:
        """Create BedrockModel instance"""
        if model_id in self._models:
            return self._models[model_id]["model"], model_id

        temperature = float(config.get("temperature", 0.7))
        max_tokens = int(config.get("maxTokens", 4096))

        model = BedrockModel(
            model_id=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
            cache_prompt="default",
        )

        self._models[model_id] = {"model": model, "model_id": model_id}
        return model, model_id

    async def run_async(self, agent_id: str, user_message: str, session_id: Optional[str] = None) -> dict:
        """Run conversation with agent"""
        agent = self.get_or_create_agent(agent_id, session_id)

        # Track conversation in memory
        memory_manager = get_memory_manager()
        session = None
        if session_id:
            session = memory_manager.get_or_create_session(session_id, agent_id)
            session.add_message("user", user_message)

        # Run agent
        result = await agent.invoke_async(user_message)
        response_text = self._extract_response_text(result)

        # Save response
        if session:
            session.add_message("assistant", response_text)

        return {"message": response_text}
```

#### MCP Manager with Strands MCPClient

```python
# src/core/mcp_manager.py
from strands.tools.mcp import MCPClient
from typing import Dict, List, Optional
import asyncio

class MCPManager:
    """Manages MCP server connections using Strands MCPClient"""

    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
        self.connection_status: Dict[str, str] = {}

    async def connect_mcp(self, config: MCPConfig) -> MCPClient:
        """Establish connection to MCP server using MCPClient"""
        try:
            if config.connection_type == "stdio":
                client = MCPClient.from_stdio_server(
                    command=config.config['command'],
                    args=config.config.get('args', [])
                )
            elif config.connection_type == "sse":
                client = MCPClient.from_sse_server(
                    url=config.config['url']
                )
            elif config.connection_type == "http":
                client = MCPClient.from_streamable_http_server(
                    url=config.config['url']
                )
            else:
                raise ValueError(f"Unsupported connection type: {config.connection_type}")

            # Test connection by listing tools
            tools = client.list_tools_sync()

            self.clients[config.name] = client
            self.connection_status[config.name] = "online"

            return client

        except Exception as e:
            self.connection_status[config.name] = "error"
            raise ConnectionError(f"Failed to connect to MCP server {config.name}: {str(e)}")

    def get_mcp_tools(self, mcp_name: str, allowed: Optional[List[str]] = None, rejected: Optional[List[str]] = None):
        """Retrieve tools from connected MCP server with optional filtering"""
        client = self.clients.get(mcp_name)
        if not client:
            raise ValueError(f"MCP server not connected: {mcp_name}")

        # Get all tools
        tools = client.list_tools_sync()

        # Apply allowed filter (whitelist)
        if allowed:
            tools = [t for t in tools if t.name in allowed]

        # Apply rejected filter (blacklist)
        if rejected:
            tools = [t for t in tools if t.name not in rejected]

        return tools

    def get_mcp_status(self, mcp_name: str) -> str:
        """Get connection status: online, offline, error"""
        return self.connection_status.get(mcp_name, "offline")

    async def disconnect_mcp(self, mcp_name: str):
        """Close MCP server connection"""
        client = self.clients.pop(mcp_name, None)
        if client:
            # MCPClient cleanup handled by context manager
            self.connection_status[mcp_name] = "offline"

    async def test_connection(self, mcp_name: str) -> Dict[str, any]:
        """Test MCP connection health"""
        client = self.clients.get(mcp_name)
        if not client:
            return {"status": "offline", "error": "Not connected"}

        try:
            tools = client.list_tools_sync()
            return {
                "status": "online",
                "tools_count": len(tools),
                "tools": [t.name for t in tools]
            }
        except Exception as e:
            self.connection_status[mcp_name] = "error"
            return {"status": "error", "error": str(e)}
```

#### Memory Manager (Simplified - In-Memory Storage)

```python
# src/core/memory_manager.py
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ConversationMessage:
    """A single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ConversationSession:
    """A conversation session with message history."""
    session_id: str
    agent_id: str
    messages: list[ConversationMessage] = field(default_factory=list)

    def add_message(self, role: str, content: str):
        self.messages.append(ConversationMessage(role=role, content=content))

    def get_history(self) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in self.messages]

class MemoryManager:
    """Simple in-memory conversation storage (no external dependencies)"""

    def __init__(self):
        self._sessions: dict[str, ConversationSession] = {}
        self.enabled = True

    def get_or_create_session(self, session_id: str, agent_id: str = "default") -> ConversationSession:
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationSession(session_id=session_id, agent_id=agent_id)
        return self._sessions[session_id]

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

# Global instance
_memory_manager: Optional[MemoryManager] = None

def get_memory_manager() -> MemoryManager:
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
```

**Note**: Conversations are stored in memory and lost on server restart. For production persistence, consider adding DynamoDB or Redis storage.

---

### 3.4 Data Layer

#### Database Schema (DynamoDB)

**DynamoDB Tables Design**

```python
# agents table
{
    "PK": "AGENT#{agent_id}",                        # Partition key
    "SK": "METADATA",                                 # Sort key
    "agent_name": str,
    "description": str,
    "model_id": str,
    "temperature": float,
    "max_tokens": int,
    "thinking_enabled": bool,
    "thinking_budget": int,
    "system_prompt": str,
    "skills": List[str],                              # List of skill IDs
    "mcp_servers": List[str],                         # List of MCP server IDs
    "agentcore_arn": str,                             # AgentCore Runtime ARN
    "deployment_status": str,                         # deployed, pending, failed
    "created_at": str,                                # ISO 8601
    "updated_at": str,
    "GSI1PK": "USER#{user_id}",                      # GSI for user queries
    "GSI1SK": "AGENT#{agent_id}"
}

# skills table
{
    "PK": "SKILL#{skill_id}",                        # Partition key
    "SK": "METADATA",                                 # Sort key
    "skill_name": str,
    "description": str,
    "s3_location": str,                               # S3 URI for ZIP package (s3://bucket/skills/skill_id.zip)
    "created_by": str,                                # User ID
    "created_at": str,
    "updated_at": str,
    "version": str,
    "is_system": bool,                                # System vs user-created
    "GSI1PK": "USER#{user_id}",                      # GSI for user queries
    "GSI1SK": "SKILL#{created_at}"
}

# mcp_servers table
{
    "PK": "MCP#{server_id}",                         # Partition key
    "SK": "CONFIG",                                   # Sort key
    "server_name": str,
    "description": str,
    "connection_type": str,                           # stdio, sse, http
    "endpoint_or_command": str,
    "config": Dict,                                   # Connection-specific config
    "status": str,                                    # online, offline, error
    "tools": List[Dict],                             # Cached tool list
    "allowed_tools": List[str],                      # Whitelist (optional)
    "rejected_tools": List[str],                     # Blacklist (optional)
    "last_health_check": str,
    "created_at": str,
    "updated_at": str,
    "GSI1PK": "USER#{user_id}",
    "GSI1SK": "MCP#{server_id}"
}

# users table
{
    "PK": "USER#{user_id}",                          # Partition key
    "SK": "PROFILE",                                  # Sort key
    "email": str,
    "hashed_password": str,
    "name": str,
    "created_at": str,
    "last_login": str,
    "GSI1PK": "EMAIL#{email}",                       # GSI for email lookup
    "GSI1SK": "USER"
}
```

**Global Secondary Indexes (GSI)**

```python
# GSI1: User-based queries
{
    "IndexName": "GSI1",
    "KeySchema": [
        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
        {"AttributeName": "GSI1SK", "KeyType": "RANGE"}
    ],
    "Projection": {"ProjectionType": "ALL"}
}

# Example queries:
# - Get all agents for user: GSI1PK = USER#{user_id}, GSI1SK begins_with AGENT#
# - Get all skills for user: GSI1PK = USER#{user_id}, GSI1SK begins_with SKILL#
# - Get all MCP servers for user: GSI1PK = USER#{user_id}, GSI1SK begins_with MCP#
```

#### Storage Strategy

**Relational Data (DynamoDB)**:
- Agent configurations and deployment status
- Skill metadata and references
- MCP server configurations
- User accounts and profiles

**File Storage (S3)**:
- Skill packages: `s3://bucket/skills/{skill_id}.zip`
  - ZIP archive containing SKILL.md (with YAML frontmatter) and assets
  - S3 URI stored in DynamoDB skills table as `s3_location` field
  - Downloaded to AgentCore Runtime filesystem at `/app/skills/{skill_name}/` during initialization
  - Versioning enabled for rollback capability
- Uploaded files: `s3://bucket/uploads/{user_id}/{file_id}`
  - User-uploaded images and documents
- Agent configuration backups: `s3://bucket/backups/agents/{agent_id}/{timestamp}.json`
- Generated artifacts: `s3://bucket/artifacts/{session_id}/{artifact_id}`

**Memory Storage (AgentCore Memory)**:
- All conversation history (short-term and long-term)
- Event-based storage with timestamps
- Semantic embeddings for context retrieval
- Automatic summarization strategies
- Cross-session memory search

---

## 4. Core Components

### 4.1 Agent Manager

**Responsibilities**:
- Instantiate and configure Strands Agent instances
- Deploy agents to AgentCore Runtime
- Manage agent lifecycle (create, update, destroy)
- Load and apply agent configurations from DynamoDB
- Coordinate tool loading (skills + MCP + built-in)
- Integrate AgentCore Memory for conversation context

**Key Methods**:
- `create_agentcore_app(config, skills, mcps) -> BedrockAgentCoreApp`
- `deploy_to_agentcore(agent_id, app) -> Dict`
- `get_agent(agent_id) -> AgentConfig`
- `list_user_agents(user_id) -> List[AgentConfig]`
- `update_agent_config(agent_id, new_config)`

---

### 4.2 Skill Manager

**Responsibilities**:
- Read skill S3 URIs from DynamoDB skills table
- Download and sync skill packages from S3 to local filesystem using boto3
- Parse SKILL.md YAML frontmatter and markdown content
- Validate skill packages structure
- Handle skill uploads (ZIP upload to S3, metadata to DynamoDB)
- Generate dynamic skill tool with available skills list
- Manage skill versioning

**Skill Loading Flow** (AgentCore Runtime):

1. **Read Configuration**: Query DynamoDB to get enabled skills and their S3 URIs
2. **Download from S3**: Use boto3 to download skill ZIP packages
3. **Extract to Filesystem**: Unzip to `/app/skills/{skill_name}/` directory
4. **Initialize Skills**: Use `init_skills()` to scan `/app/skills/` and parse SKILL.md files
5. **Generate Tool**: Create dynamic `Skill` tool with all available skills in docstring
6. **Runtime Loading**: When invoked, `load_skill()` reads full SKILL.md content and injects into conversation

**Key Methods**:
- `sync_skills_from_s3(agent_config) -> None` - Download enabled skills to local filesystem
- `init_skills() -> str` - Scan skills directory and generate skill list XML
- `load_skill(command) -> List[Dict]` - Load full skill prompt content
- `generate_skill_tool() -> Tool` - Create dynamic Strands tool with skill registry
- `upload_skill_to_s3(zip_file, skill_id) -> str` - Upload ZIP to S3 and save metadata to DynamoDB

**Implementation Reference**: See `src/skill_tool.py` for:
- YAML frontmatter parsing (name, description)
- Skill discovery from filesystem
- Dynamic tool generation with `@tool` decorator
- Hook-based skill content injection using `SkillToolInterceptor`

---

### 4.3 MCP Manager

**Responsibilities**:
- Establish connections to MCP servers using Strands MCPClient
- Support multiple connection types (stdio, SSE, HTTP)
- Retrieve tool definitions from MCP servers
- Handle MCP protocol communication
- Manage connection lifecycle and health monitoring
- Apply tool filtering (allowed/rejected lists)

**Key Methods**:
- `connect_mcp(config) -> MCPClient`
- `get_mcp_tools(mcp_name, allowed, rejected) -> List[Tool]`
- `disconnect_mcp(mcp_name)`
- `test_connection(mcp_name) -> Dict`
- `get_mcp_status(mcp_name) -> str`

---

### 4.4 Memory Manager

**Responsibilities**:
- Manage AgentCore Memory sessions
- Store conversation turns with semantic embeddings
- Search long-term memories using semantic queries
- Retrieve conversation context for agent invocations
- Implement memory retention strategies

**Key Methods**:
- `create_session(actor_id, session_id) -> MemorySession`
- `save_conversation(actor_id, session_id, user_msg, assistant_msg)`
- `search_memories(actor_id, session_id, query, max_results) -> List[Dict]`

---

### 4.5 Streaming Handler

**Responsibilities**:
- Coordinate async streaming from AgentCore Runtime
- Transform SDK events to WebSocket messages
- Handle backpressure and buffering
- Manage WebSocket connections

**Event Types**:
- `thinking`: Extended thinking content
- `text`: Incremental response text
- `tool_use`: Tool invocation details
- `tool_result`: Tool execution results
- `error`: Error messages
- `memory_update`: Memory storage confirmation

---

## 5. Data Models

### 5.1 Agent Configuration

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

class AgentConfig(BaseModel):
    id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    model_id: str = Field(
        default="anthropic.claude-sonnet-4-5-20250929-v1:0",
        description="Bedrock model identifier"
    )
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=256, le=24000)
    thinking_enabled: bool = Field(default=False)
    thinking_budget: int = Field(default=1024, ge=256, le=4096)
    system_prompt: Optional[str] = None
    skill_ids: List[str] = Field(default_factory=list)
    mcp_ids: List[str] = Field(default_factory=list)
    agentcore_arn: Optional[str] = None
    deployment_status: str = Field(default="pending")  # pending, deployed, failed

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Data Analyst Agent",
                "description": "Specialized in data analysis and visualization",
                "model_id": "anthropic.claude-sonnet-4-5-20250929-v1:0",
                "temperature": 0.7,
                "max_tokens": 8000,
                "thinking_enabled": True,
                "thinking_budget": 2048,
                "skill_ids": ["xlsx-skill", "docx-skill"],
                "mcp_ids": ["postgres-mcp"]
            }
        }
```

### 5.2 Skill Definition

```python
class SkillMetadata(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: str
    s3_location: str  # S3 URI
    created_by: str  # User ID
    created_at: Optional[str] = None
    version: str = Field(default="1.0.0")
    is_system: bool = Field(default=False)

class SkillUploadRequest(BaseModel):
    name: str
    file: UploadFile  # FastAPI type

class SkillGenerateRequest(BaseModel):
    description: str = Field(
        ...,
        description="Natural language description of the skill to generate"
    )
    examples: Optional[List[str]] = None
```

### 5.3 MCP Server Configuration

```python
class MCPConfig(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    connection_type: Literal["stdio", "sse", "http"]
    config: Dict[str, Any] = Field(
        ...,
        description="Connection-specific configuration"
    )
    allowed_tools: Optional[List[str]] = None  # Whitelist
    rejected_tools: Optional[List[str]] = None  # Blacklist
    status: str = Field(default="offline")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "PostgreSQL MCP",
                "description": "Database query tool",
                "connection_type": "stdio",
                "config": {
                    "command": "uvx",
                    "args": ["mcp-server-postgres", "postgresql://..."]
                },
                "allowed_tools": ["query_database", "list_tables"]
            }
        }
```

### 5.4 Message Structures

```python
class Message(BaseModel):
    id: Optional[str] = None
    conversation_id: str
    role: Literal["user", "assistant"]
    content: List[ContentBlock]
    thinking_content: Optional[str] = None
    tool_uses: Optional[List[ToolUse]] = None
    created_at: Optional[str] = None

class ContentBlock(BaseModel):
    type: Literal["text", "image", "tool_use", "tool_result"]
    text: Optional[str] = None
    image: Optional[ImageSource] = None
    tool_use: Optional[ToolUse] = None
    tool_result: Optional[ToolResult] = None

class ImageSource(BaseModel):
    type: Literal["base64", "url"]
    media_type: str  # e.g., "image/jpeg"
    data: str

class ToolUse(BaseModel):
    id: str
    name: str
    input: Dict[str, Any]

class ToolResult(BaseModel):
    tool_use_id: str
    content: List[ContentBlock]
    is_error: bool = False
```

### 5.5 Memory Query

```python
class MemorySearchRequest(BaseModel):
    actor_id: str
    session_id: str
    query: str
    max_results: int = Field(default=5, ge=1, le=20)
    namespace_prefix: Optional[str] = None

class MemorySearchResponse(BaseModel):
    memories: List[Dict[str, Any]]
    total_count: int
```

---

## 6. API Design

### 6.1 REST Endpoints

#### Agent Endpoints

```
GET    /api/agents                    # List all agents for current user
GET    /api/agents/{agent_id}         # Get specific agent
POST   /api/agents                    # Create new agent
PUT    /api/agents/{agent_id}         # Update agent
DELETE /api/agents/{agent_id}         # Delete agent
POST   /api/agents/{agent_id}/deploy  # Deploy to AgentCore Runtime
GET    /api/agents/default            # Get default system agent
```

**Example: Deploy Agent to AgentCore**

```http
POST /api/agents/{agent_id}/deploy
Content-Type: application/json
Authorization: Bearer <token>

Response: 200 OK
{
  "status": "deployed",
  "agent_id": "agent-uuid",
  "agentcore_arn": "arn:aws:bedrock:us-west-2:account:agent/agent-uuid",
  "endpoint": "https://agentcore.bedrock.us-west-2.amazonaws.com/agents/agent-uuid",
  "deployed_at": "2025-11-01T10:30:00Z"
}
```

#### Skill Endpoints

```
GET    /api/skills                    # List all skills
GET    /api/skills/{skill_id}         # Get specific skill
POST   /api/skills/upload             # Upload skill ZIP
POST   /api/skills/generate           # AI-generate skill using agent
DELETE /api/skills/{skill_id}         # Delete skill
GET    /api/skills/system             # List system-provided skills
```

**Example: AI-Generate Skill**

```http
POST /api/skills/generate
Content-Type: application/json
Authorization: Bearer <token>

{
  "skill_description": "A skill that can read and analyze Excel files, extract data from specific sheets and cells, and generate summary statistics",
  "skill_name": "excel-analyzer",
  "assets_needed": ["sample.xlsx"]
}

Response: 200 OK
{
  "skill_id": "excel-analyzer-001",
  "skill_name": "excel-analyzer",
  "description": "Read and analyze Excel files with data extraction and statistics",
  "s3_location": "s3://platform-bucket/skills/excel-analyzer-001.zip",
  "status": "generated",
  "created_at": "2025-10-31T15:30:00Z",
  "preview_url": "/api/skills/excel-analyzer-001/preview"
}
```

#### MCP Endpoints

```
GET    /api/mcp                       # List all MCP servers
GET    /api/mcp/{mcp_id}              # Get specific MCP server
POST   /api/mcp                       # Create MCP server config
PUT    /api/mcp/{mcp_id}              # Update MCP server
DELETE /api/mcp/{mcp_id}              # Delete MCP server
POST   /api/mcp/{mcp_id}/test         # Test MCP connection
GET    /api/mcp/{mcp_id}/tools        # List available tools
```

**Example: Test MCP Connection**

```http
POST /api/mcp/{mcp_id}/test
Authorization: Bearer <token>

Response: 200 OK
{
  "status": "online",
  "tools_count": 5,
  "tools": ["read_file", "write_file", "list_directory", "search", "replace"],
  "latency_ms": 45
}
```

#### Memory Endpoints

```
POST   /api/memory/search             # Search AgentCore Memory (semantic search)
GET    /api/memory/history            # Get conversation history from AgentCore Memory
```

**Note**: All conversation history is stored in AgentCore Memory, not DynamoDB. The `/history` endpoint retrieves recent turns from AgentCore Memory service.

**Example: Search Memory**

```http
POST /api/memory/search
Content-Type: application/json
Authorization: Bearer <token>

{
  "actor_id": "user-123",
  "session_id": "session-456",
  "query": "previous discussions about database optimization",
  "max_results": 5
}

Response: 200 OK
{
  "memories": [
    {
      "content": "We discussed indexing strategies for PostgreSQL...",
      "timestamp": "2025-10-31T14:20:00Z",
      "relevance_score": 0.92
    },
    {
      "content": "Query optimization techniques included...",
      "timestamp": "2025-10-30T09:15:00Z",
      "relevance_score": 0.87
    }
  ],
  "total_count": 5
}
```

**Example: Get Conversation History**

```http
GET /api/memory/history?actor_id=user-123&session_id=session-456&limit=20
Authorization: Bearer <token>

Response: 200 OK
{
  "history": [
    {
      "role": "user",
      "content": "How do I optimize database queries?",
      "timestamp": "2025-10-31T14:18:00Z"
    },
    {
      "role": "assistant",
      "content": "Here are some key strategies for optimizing database queries...",
      "timestamp": "2025-10-31T14:18:15Z"
    },
    {
      "role": "user",
      "content": "What about indexing?",
      "timestamp": "2025-10-31T14:20:00Z"
    },
    {
      "role": "assistant",
      "content": "Indexing is crucial for query performance...",
      "timestamp": "2025-10-31T14:20:30Z"
    }
  ],
  "session_id": "session-456",
  "total_turns": 4
}
```

### 6.2 WebSocket Protocol (Chat)

**Connection Endpoint**: `ws://api.example.com/api/chat/stream`

**Authentication**: Send JWT token in first message

**Client → Server Messages**:

```json
// Initial authentication
{
  "type": "auth",
  "token": "<jwt-token>"
}

// Start conversation with agent
{
  "type": "start_conversation",
  "agent_id": "<agent-uuid>",
  "actor_id": "<user-id>",
  "session_id": "<session-uuid>"
}

// Note: Skills and MCPs are fetched from agent configuration in DynamoDB

// Send user message
{
  "type": "user_message",
  "conversation_id": "<conversation-uuid>",
  "content": [
    {
      "type": "text",
      "text": "Analyze this data"
    }
  ]
}
```

**Server → Client Messages**:

```json
// Connection confirmed
{
  "type": "connected",
  "session_id": "<session-uuid>"
}

// Memory context retrieved
{
  "type": "memory_context",
  "session_id": "<session-uuid>",
  "memories_count": 3
}

// Thinking content (if enabled)
{
  "type": "thinking",
  "session_id": "<session-uuid>",
  "data": "Analyzing the user's request..."
}

// Incremental text response
{
  "type": "text",
  "session_id": "<session-uuid>",
  "data": "I'll help you analyze "
}

// Tool use event
{
  "type": "tool_use",
  "session_id": "<session-uuid>",
  "data": {
    "id": "toolu_123",
    "name": "Skill",
    "input": {
      "command": "xlsx"
    }
  }
}

// Memory saved
{
  "type": "memory_saved",
  "session_id": "<session-uuid>",
  "timestamp": "2025-11-01T10:35:00Z"
}

// Response complete
{
  "type": "message_complete",
  "session_id": "<session-uuid>",
  "message_id": "<message-uuid>"
}
```

---

## 7. Technology Stack

### Frontend

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Framework | React 18+ | Component-based, rich ecosystem |
| Build Tool | Vite | Fast HMR, optimized builds |
| Language | TypeScript | Type safety, better DX |
| Styling | Tailwind CSS | Rapid styling, consistency, dark mode support |
| Design System | Space Grotesk font + Material Symbols | Modern, clean aesthetic matching UI designs |
| State Management | TanStack Query | Server state caching, automatic refetching |
| Routing | React Router v6 | Standard routing solution |
| WebSocket | native WebSocket API | Built-in browser support |
| HTTP Client | Axios | Interceptors, request cancellation |

### Backend

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Framework | FastAPI | Async support, auto-generated docs |
| ASGI Server | Uvicorn | High performance, SSE support |
| Agent SDK | Strands Agents | Native AWS Bedrock integration |
| Agent Runtime | In-process (FastAPI) | Simplified, no external dependencies |
| Memory | In-memory dict | Simple session storage |
| Database | DynamoDB | Serverless, scalable, single-digit ms latency |
| Storage | AWS S3 | Scalable object storage (optional) |
| Validation | Pydantic v2 | FastAPI native, runtime validation |

### AI/ML Services

| Component | Service | Models |
|-----------|---------|--------|
| LLM Provider | AWS Bedrock | Claude Sonnet 4.5, Haiku 4.5 |
| Agent Execution | Strands Agent SDK | Runs in FastAPI process |
| Memory | In-memory storage | Session-based conversation history |
| MCP Client | Strands MCPClient | stdio, SSE, HTTP connections |
| Search | Tavily API | Web search capabilities (optional) |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containerization | Docker | Consistent environments |
| Backend Orchestration | ECS Fargate | Serverless containers for FastAPI |
| Load Balancer | ALB | Traffic distribution and frontend/backend routing |
| Secrets | AWS Secrets Manager | Secure credential storage |
| Monitoring | CloudWatch | Logs, metrics, traces |

---

## 8. Deployment Architecture

### 8.1 AWS Deployment (Simplified Production)

```
Internet
   │
   ▼
[ALB: Application Load Balancer]
   │
   ├────────► [S3: React Static Files]
   │           • index.html
   │           • JS/CSS bundles
   │           • Assets
   │
   └────────► [ECS Fargate: FastAPI Backend]
               • REST API endpoints
               • SSE streaming
               • Strands Agent (runs in-process)
               • In-memory conversation storage
               │
               ├─► [DynamoDB Tables]
               │    • agents
               │    • skills
               │    • mcp_servers
               │
               ├─► [AWS Bedrock]
               │    • Claude Sonnet 4.5
               │    • Claude Haiku 4.5
               │
               └─► [MCP Servers] (optional)
                    • External tools
                    • API integrations
```

**Key Simplifications**:
- No AgentCore Runtime - agents run directly in ECS Fargate containers
- No AgentCore Memory - conversations stored in-memory (or add DynamoDB for persistence)
- SSE streaming instead of WebSocket

### 8.2 Component Deployment Details

**Frontend (S3 Static Website Hosting)**:
- Static React build deployed to S3
- S3 static website hosting enabled
- Served through ALB for unified endpoint
- Simple and cost-effective deployment

**Backend API (ECS Fargate)**:
- FastAPI application in Docker container
- **Agents run directly in-process** (no external runtime)
- Auto-scaling based on CPU/memory
- ALB for load distribution
- VPC with private subnets for security
- Security groups for controlled access

**Deployment Model (Simplified)**:
1. User creates agent configuration via UI → saved to DynamoDB
2. User sends message → FastAPI loads agent config and creates Strands Agent in-process
3. Strands Agent invokes Bedrock Claude models directly
4. Response streamed back via SSE

**Conversation Storage**:
- In-memory storage (default) - conversations lost on restart
- For persistence: add DynamoDB or Redis storage in MemoryManager

**Data Layer**:
- DynamoDB tables with on-demand capacity
- S3 buckets for skill storage (optional)

### 8.3 Deployment Steps

**1. Deploy FastAPI Backend to ECS Fargate**

```bash
# Build Docker image
docker build -t agent-platform-api:latest .

# Push to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com
docker tag agent-platform-api:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/agent-platform-api:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/agent-platform-api:latest

# Deploy to ECS Fargate
aws ecs update-service \
  --cluster agent-platform-cluster \
  --service api-service \
  --force-new-deployment
```

**2. Deploy React Frontend to S3**

```bash
# Build React app
cd frontend
npm run build

# Deploy to S3 with static website hosting
aws s3 sync dist/ s3://agent-platform-frontend/ --delete

# Enable static website hosting
aws s3 website s3://agent-platform-frontend/ \
  --index-document index.html \
  --error-document index.html
```

**3. Create DynamoDB Tables**

```bash
# Create agents table
aws dynamodb create-table \
  --table-name agents \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
    AttributeName=GSI1PK,AttributeType=S \
    AttributeName=GSI1SK,AttributeType=S \
  --key-schema \
    AttributeName=PK,KeyType=HASH \
    AttributeName=SK,KeyType=RANGE \
  --global-secondary-indexes \
    "IndexName=GSI1,KeySchema=[{AttributeName=GSI1PK,KeyType=HASH},{AttributeName=GSI1SK,KeyType=RANGE}],Projection={ProjectionType=ALL}" \
  --billing-mode PAY_PER_REQUEST

# Repeat for skills, mcp_servers, users tables
```

**4. Deploy Agents to AgentCore Runtime**

```bash
# Deploy agent using AgentCore CLI
agentcore launch \
  --agent-id <agent-uuid> \
  --region us-west-2 \
  --memory-id <memory-id> \
  --environment production

# Verify deployment
agentcore describe --agent-id <agent-uuid>
```

**5. Configure AgentCore Memory**

```python
# Initialize memory with semantic strategy
from bedrock_agentcore.memory import MemorySessionManager

memory_manager = MemorySessionManager(
    memory_id="agent-platform-memory",
    region_name="us-west-2"
)

# Memory is automatically configured with:
# - Event storage for all conversation turns
# - Semantic embeddings for searchability
# - Configurable retention policies
```

**6. Set up MCP Server Connections**

```python
# MCP servers are configured per-agent via DynamoDB
# Connection established on-demand when agent is invoked
# Status monitored via health checks

# Example: Configure filesystem MCP
mcp_config = {
    "name": "filesystem-mcp",
    "connection_type": "stdio",
    "config": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    }
}
```

### 8.4 Infrastructure as Code (Terraform)

```hcl
# terraform/main.tf

# DynamoDB Tables
resource "aws_dynamodb_table" "agents" {
  name           = "agents"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "PK"
  range_key      = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "GSI1PK"
    type = "S"
  }

  attribute {
    name = "GSI1SK"
    type = "S"
  }

  global_secondary_index {
    name            = "GSI1"
    hash_key        = "GSI1PK"
    range_key       = "GSI1SK"
    projection_type = "ALL"
  }

  tags = {
    Environment = "production"
    Project     = "agent-platform"
  }
}

# S3 Bucket for Skills
resource "aws_s3_bucket" "skills" {
  bucket = "agent-platform-skills"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    enabled = true

    noncurrent_version_expiration {
      days = 90
    }
  }
}

# ECS Cluster for FastAPI
resource "aws_ecs_cluster" "api_cluster" {
  name = "agent-platform-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

```

### 8.5 Container Configuration

**Dockerfile (Backend)**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install AgentCore SDK
RUN pip install bedrock-agentcore strands-agents

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose (Local Development)**:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_WS_URL=ws://localhost:8000
    depends_on:
      - backend

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
      - ./skills:/app/skills
    environment:
      - AWS_REGION=us-west-2
      - DYNAMODB_ENDPOINT=http://dynamodb-local:8000
      - S3_BUCKET=agent-platform-skills
      - AGENTCORE_MEMORY_ID=local-memory-test
    env_file:
      - .env
    depends_on:
      - dynamodb-local

  dynamodb-local:
    image: amazon/dynamodb-local:latest
    ports:
      - "8001:8000"
    command: "-jar DynamoDBLocal.jar -sharedDb -dbPath /data"
    volumes:
      - dynamodb_data:/data

volumes:
  dynamodb_data:
```

---

## 9. Security & Best Practices

### 9.1 Authentication & Authorization

**Strategy**: JWT-based authentication with AWS Cognito integration

```python
# src/api/middleware/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserContext:
    """Verify JWT token and extract user context"""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return UserContext(user_id=user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Usage in endpoints
@app.get("/api/agents")
async def list_agents(user: UserContext = Depends(verify_token)):
    return await get_user_agents(user.user_id)
```

### 9.2 DynamoDB Security

**IAM Policies**:
- Least privilege access for API service
- Separate read/write permissions
- Attribute-level access control

**Data Encryption**:
- Encryption at rest using AWS KMS
- Encryption in transit using TLS
- Point-in-time recovery enabled

### 9.3 AgentCore Security

**Execution Isolation**:
- Each agent runs in isolated AgentCore Runtime
- Automatic resource limits and timeouts
- Network isolation for sensitive operations

**Memory Access Control**:
- Actor-based memory isolation
- Session-level access control
- Encrypted storage of conversation data

### 9.4 MCP Security

**Connection Validation**:
- Verify MCP server identity
- TLS for HTTP/SSE connections
- Command validation for stdio connections

**Tool Filtering**:
- Whitelist allowed tools per MCP server
- Blacklist dangerous operations
- Regex-based filtering for tool names

```python
# Example: Configure MCP with security filters
mcp_config = {
    "name": "filesystem-mcp",
    "connection_type": "stdio",
    "config": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/safe-workspace"]
    },
    "allowed_tools": ["read_file", "list_directory"],  # Whitelist only safe operations
    "rejected_tools": ["delete_file", "execute_command"]  # Blacklist dangerous operations
}
```

### 9.5 Input Validation

**Comprehensive validation using Pydantic**:

```python
from pydantic import BaseModel, validator, Field
import re

class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    model_id: str
    max_tokens: int = Field(ge=256, le=24000)

    @validator("name")
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError("Name contains invalid characters")
        return v

    @validator("model_id")
    def validate_model(cls, v):
        allowed_models = [
            "anthropic.claude-sonnet-4-5-20250929-v1:0",
            "anthropic.claude-haiku-4-5-20251001-v1:0"
        ]
        if v not in allowed_models:
            raise ValueError(f"Invalid model. Allowed: {allowed_models}")
        return v
```

### 9.6 Secrets Management

**Never hardcode credentials**:

```python
# src/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # AWS
    aws_region: str = "us-west-2"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    # JWT
    jwt_secret: str
    jwt_expiry_hours: int = 24

    # DynamoDB
    dynamodb_table_agents: str = "agents"
    dynamodb_table_skills: str = "skills"

    # S3
    s3_bucket_skills: str

    # Redis
    redis_url: str

    # AgentCore
    agentcore_memory_id: str

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

**Production**: Use AWS Secrets Manager

```python
import boto3
import json

def get_secret(secret_name: str) -> dict:
    client = boto3.client('secretsmanager', region_name='us-west-2')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])
```

---

## 10. Performance & Scalability

### 10.1 Caching Strategy

**Multi-Layer Caching**:

1. **Prompt Caching (Bedrock)**:
   - System prompts cached at model level
   - Skill content cached (reduces token costs by 90%)
   - Tool definitions cached
   - Context window optimization

2. **Memory Caching (AgentCore Memory)**:
   - Recent conversation turns cached in-memory
   - Semantic embeddings cached for fast retrieval
   - Automatic cache invalidation

**Note**: To reduce infrastructure costs:
- Application-level caching (Redis) has been removed
- CDN (CloudFront) has been removed
- Agent configurations and metadata are fetched directly from DynamoDB with optimized queries and low-latency access patterns
- Static assets are served directly from S3 through ALB

### 10.2 DynamoDB Optimization

**Capacity Planning**:
- Use on-demand billing for unpredictable workloads
- Auto-scaling for provisioned capacity if predictable

**Query Optimization**:
- Use GSIs for efficient user-based queries
- Batch operations for bulk reads/writes
- Sparse indexes for optional attributes
- Composite sort keys for complex queries

**Example Efficient Query**:

```python
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('agents')

# Efficient query using GSI
response = table.query(
    IndexName='GSI1',
    KeyConditionExpression=Key('GSI1PK').eq(f'USER#{user_id}') & Key('GSI1SK').begins_with('AGENT#')
)
agents = response['Items']
```

### 10.3 AgentCore Scalability

**Automatic Scaling**:
- AgentCore Runtime scales automatically based on demand
- No need to manage instances or containers
- Built-in load balancing and failover

**Cost Optimization**:
- Pay only for actual agent execution time
- No idle costs for unused agents
- Efficient resource allocation

### 10.4 WebSocket Optimization

**Connection Management**:
- Implement heartbeat/ping-pong (every 30s)
- Automatic reconnection on client side
- Connection pooling on server side
- Graceful degradation

**Backpressure Handling**:
- Buffer size limits (10MB max)
- Slow consumer detection
- Rate limiting per user

---

## 11. Future Enhancements

### Phase 2 Features

1. **Multi-Modal Inputs**:
   - PDF upload and parsing
   - Audio input (speech-to-text via Bedrock)
   - Video frame analysis
   - OCR for scanned documents

2. **Collaborative Features**:
   - Share agents with team members (RBAC)
   - Public skill marketplace
   - Agent templates library
   - Community-contributed MCP servers

3. **Advanced Conversation Management**:
   - Branch conversations (explore alternatives)
   - Conversation search using AgentCore Memory
   - Export conversations (PDF, Markdown, JSON)
   - Conversation summarization

4. **Enhanced Observability**:
   - Token usage analytics dashboard
   - Agent performance metrics (latency, success rate)
   - Cost tracking per agent/conversation
   - AgentCore Observability integration
   - Custom metrics and alerts

5. **RAG Integration**:
   - Vector database integration (OpenSearch Serverless)
   - Document ingestion pipeline
   - Knowledge base per agent
   - Hybrid search (keyword + semantic)

### Phase 3 Features

1. **Multi-Agent Workflows**:
   - Agent chaining (output → input)
   - Parallel agent execution
   - Conditional routing based on outputs
   - Agent orchestration patterns (swarm, hierarchy)

2. **Fine-Tuning Support**:
   - Collect training data from conversations
   - Submit fine-tuning jobs to Bedrock
   - Compare base vs. fine-tuned models
   - A/B testing framework

3. **Advanced MCP Features**:
   - MCP server marketplace
   - Custom MCP server builder UI
   - MCP server health monitoring dashboard
   - Version management for MCP servers

4. **Enterprise Features**:
   - SSO integration (SAML, OAuth, Cognito)
   - Role-based access control (RBAC)
   - Audit logging (CloudTrail integration)
   - Compliance reporting (SOC 2, GDPR)
   - Multi-tenancy support

---

## Appendix

### A. Technology Alternatives Considered

| Decision | Chosen | Alternative | Rationale |
|----------|--------|-------------|-----------|
| Frontend Framework | React | Vue, Svelte | Ecosystem, team expertise, UI design compatibility |
| Backend Framework | FastAPI | Flask, Django | Async support, auto-docs, Pydantic integration |
| Database | DynamoDB | PostgreSQL, MongoDB | Serverless, scalable, single-digit latency, AWS integration |
| Agent Runtime | AgentCore Runtime | ECS, Lambda | Serverless, managed, built-in memory, no cold starts |
| Memory | AgentCore Memory | Self-managed vector DB | Managed, semantic search, event storage, AWS integration |

### B. Key Dependencies

**Backend**:
```
strands-agents==1.2.0
bedrock-agentcore==1.0.0
fastapi==0.110.0
uvicorn[standard]==0.27.0
boto3==1.34.0
aioboto3==12.0.0
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
```

**Frontend**:
```json
{
  "react": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "@tanstack/react-query": "^5.14.0",
  "axios": "^1.6.2",
  "tailwindcss": "^3.3.0",
  "typescript": "^5.3.0"
}
```

### C. Monitoring & Logging Strategy

**CloudWatch Logs**:
- Application logs (INFO, WARNING, ERROR)
- Access logs (HTTP requests)
- WebSocket connection logs
- AgentCore Runtime logs (automatic)

**CloudWatch Metrics**:
- Request count, latency percentiles
- WebSocket connections (active, total)
- Error rates by endpoint
- Bedrock API latency and errors
- DynamoDB read/write capacity

**AgentCore Observability**:
- Agent invocation traces
- Tool execution metrics
- Memory search latency
- Token usage per agent
- Error rates and types

**Custom Metrics**:
- Agent invocations per user
- Average conversation length
- Cost per agent/conversation
- Skill invocation frequency
- MCP connection health

**Alerts**:
- Error rate > 5% (5 min window)
- P99 latency > 10s
- WebSocket connection failures > 10/min
- Bedrock throttling errors
- DynamoDB capacity exceeded
- AgentCore deployment failures

### D. Code Examples

**Skill Loading from S3 to AgentCore Runtime**:

```python
# Example: Complete skill loading flow in AgentCore Runtime
import boto3
import zipfile
import tempfile
from pathlib import Path

def sync_skills_from_dynamodb_and_s3(agent_config: dict, boto_session: boto3.Session):
    """
    Complete example of syncing skills from DynamoDB/S3 to AgentCore Runtime filesystem

    This function demonstrates the pattern described in the architecture:
    1. Read skill IDs from agent configuration
    2. Query DynamoDB for skill metadata (including S3 URI)
    3. Download skill ZIP from S3 using boto3
    4. Extract to /app/skills/{skill_name}/ directory
    5. Initialize skills using src/skill_tool.py patterns
    """

    # Step 1: Get enabled skills from agent configuration
    skill_ids = agent_config.get('skills', [])  # e.g., ['xlsx-skill', 'pdf-skill']

    dynamodb = boto_session.resource('dynamodb')
    s3_client = boto_session.client('s3')
    skills_table = dynamodb.Table('skills')

    skills_dir = Path('/app/skills')
    skills_dir.mkdir(parents=True, exist_ok=True)

    for skill_id in skill_ids:
        # Step 2: Query DynamoDB for skill metadata
        response = skills_table.get_item(
            Key={
                'PK': f'SKILL#{skill_id}',
                'SK': 'METADATA'
            }
        )

        if 'Item' not in response:
            print(f"⚠️ Skill {skill_id} not found in DynamoDB")
            continue

        skill = response['Item']
        skill_name = skill['skill_name']      # e.g., 'xlsx'
        s3_location = skill['s3_location']    # e.g., 's3://platform-bucket/skills/xlsx-skill.zip'

        # Parse S3 URI (s3://bucket/key)
        s3_parts = s3_location.replace('s3://', '').split('/', 1)
        bucket = s3_parts[0]
        key = s3_parts[1]

        # Step 3: Download ZIP from S3
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            print(f"📥 Downloading {skill_name} from {s3_location}")
            s3_client.download_file(bucket, key, tmp_file.name)

            # Step 4: Extract to /app/skills/{skill_name}/
            skill_path = skills_dir / skill_name
            skill_path.mkdir(exist_ok=True)

            with zipfile.ZipFile(tmp_file.name, 'r') as zip_ref:
                zip_ref.extractall(skill_path)

            print(f"✅ Extracted to {skill_path}")

        # Validate SKILL.md exists
        skill_md = skill_path / 'SKILL.md'
        if not skill_md.exists():
            print(f"❌ SKILL.md not found in {skill_path}")
            continue

        # Preview SKILL.md structure
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()[:200]
            print(f"📄 SKILL.md preview:\n{content}...")

    # Step 5: Initialize skills using skill_tool.py pattern
    from src.skill_tool import generate_skill_tool, SkillToolInterceptor

    # Generate dynamic skill tool (scans /app/skills/)
    skill_tool = generate_skill_tool()

    # Create hook interceptor for skill content injection
    skill_interceptor = SkillToolInterceptor()

    print(f"✅ All {len(skill_ids)} skills loaded and ready")

    return skill_tool, skill_interceptor

# Usage in AgentCore entrypoint
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel

app = BedrockAgentCoreApp()

@app.entrypoint
async def handler(event, context):
    # Get agent configuration (passed in event or from environment)
    agent_config = event.get('agent_config', {
        'skills': ['xlsx-skill', 'pdf-skill', 'docx-skill']
    })

    # Sync skills from S3
    boto_session = boto3.Session()
    skill_tool, skill_interceptor = sync_skills_from_dynamodb_and_s3(
        agent_config,
        boto_session
    )

    # Create agent with skill tool
    model = BedrockModel(
        model_id="anthropic.claude-sonnet-4-5-20250929-v1:0",
        max_tokens=8000,
        cache_prompt="default",
        cache_tools="default"
    )

    agent = Agent(
        model=model,
        tools=[skill_tool],  # Dynamic skill tool with all loaded skills
        hooks=[skill_interceptor]  # Hook for skill content injection
    )

    # Handle user request
    user_input = event['prompt']
    response = await agent.astream(user_input)

    return response
```

**Complete Agent with AgentCore Memory**:

```python
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemorySessionManager, ConversationalMessage, MessageRole

# Initialize AgentCore app
app = BedrockAgentCoreApp()

# Setup memory
memory_manager = MemorySessionManager(
    memory_id="agent-platform-memory-prod",
    region_name="us-west-2"
)

# Create model
model = BedrockModel(
    model_id="anthropic.claude-sonnet-4-5-20250929-v1:0",
    max_tokens=8000,
    temperature=0.7,
    cache_prompt="default",
    cache_tools="default"
)

# Load MCP tools
mcp_client = MCPClient.from_stdio_server(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
)
mcp_tools = mcp_client.list_tools_sync()

# Create agent
agent = Agent(
    model=model,
    tools=[*mcp_tools, skill_tool],
    system_prompt="You are a helpful AI assistant with access to files and custom skills."
)

@app.entrypoint
async def handler(event, context):
    """
    AgentCore entrypoint handler

    Event structure:
    {
        "prompt": "User message",
        "session_id": "session-123",
        "actor_id": "user-456"
    }
    """
    user_input = event['prompt']
    session_id = event['session_id']
    actor_id = event['actor_id']

    # Create memory session
    session = memory_manager.create_memory_session(actor_id, session_id)

    # Retrieve relevant context from long-term memory
    memories = session.search_long_term_memories(
        query=user_input,
        namespace_prefix=f"agent/{actor_id}/{session_id}",
        max_results=5
    )

    # Build context from memories
    context = ""
    if memories:
        context = "\n\nRelevant context from previous conversations:\n"
        for memory in memories:
            context += f"- {memory['content']}\n"

    # Run agent with streaming
    full_response = ""
    async for chunk in agent.astream(context + "\n\n" + user_input):
        full_response += chunk
        yield chunk

    # Save conversation to AgentCore Memory
    session.add_turns([
        ConversationalMessage(user_input, MessageRole.USER),
        ConversationalMessage(full_response, MessageRole.ASSISTANT)
    ])

    return {
        "response": full_response,
        "memories_used": len(memories),
        "timestamp": datetime.utcnow().isoformat()
    }

# Run the application
if __name__ == "__main__":
    app.run()
```

**Deploy to AgentCore**:

```bash
# Deploy using AgentCore CLI
agentcore launch \
  --agent-id my-agent-001 \
  --region us-west-2 \
  --memory-id agent-platform-memory-prod \
  --environment production \
  --python-version 3.11

# Verify deployment
agentcore describe --agent-id my-agent-001

# Invoke agent
agentcore invoke \
  --agent-id my-agent-001 \
  --payload '{"prompt": "Hello, how are you?", "session_id": "test-session", "actor_id": "user-123"}'
```

---

## Conclusion

This simplified architecture provides a practical AI agent platform using the Strands Agents SDK with agents running directly in the FastAPI backend. Key architectural decisions include:

1. **Simplified Design**: Agents run in-process, eliminating external runtime dependencies
2. **In-Memory Storage**: Simple session-based conversation storage (with optional DynamoDB persistence)
3. **Scalable Data Layer**: DynamoDB provides single-digit millisecond latency with automatic scaling
4. **Flexible Tool Integration**: Strands MCPClient enables seamless integration with external tools via MCP protocol
5. **Modern Frontend**: React-based UI with Tailwind CSS and SSE streaming
6. **Cost Optimization**: No additional AWS services for agent runtime

**Trade-offs**:
- Conversations are lost on server restart (unless DynamoDB persistence is added)
- No automatic agent scaling beyond ECS auto-scaling
- No semantic search across conversations (would require vector database)

**Next Steps**:
1. Review and approve architecture design
2. Set up AWS infrastructure (ECS, DynamoDB, S3)
3. Deploy FastAPI backend with Strands Agents
4. Build and deploy React frontend
5. Set up monitoring with CloudWatch
6. Optional: Add DynamoDB persistence for conversation history

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-01 | Architecture Team | Initial design document |
| 2.0 | 2025-11-01 | Architecture Team | Updated with AgentCore Runtime, AgentCore Memory, DynamoDB |
| 3.0 | 2025-12-15 | Architecture Team | **Simplified**: Removed AgentCore Runtime/Memory, agents run in-process |

**Review & Approval**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Technical Architect | TBD | | |
| Lead Engineer | TBD | | |
| Product Manager | TBD | | |
