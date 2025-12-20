# AI Agent Platform

A full-stack AI Agent Platform for managing and interacting with customizable AI agents powered by Claude Agent SDK.

## Overview

This platform enables users to:
- **Chat with AI Agents**: Interactive chat interface with SSE streaming
- **Manage Agents**: Create, configure, and monitor AI agents
- **Manage Skills**: Upload and generate custom skills
- **Manage MCP Servers**: Configure Model Context Protocol server connections

## Tech Stack

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS 4.x (styling)
- TanStack Query (state management)
- React Router v6 (routing)
- Axios (HTTP client)

### Backend
- FastAPI (Python web framework)
- Uvicorn (ASGI server)
- Pydantic v2 (data validation)
- Mock Database (in-memory for demo)

## Project Structure

```
awesome-skills-claude-agents/
├── ARCHITECTURE.md          # System architecture documentation
├── DEVELOPMENT_PLAN.md      # Development plan and roadmap
├── README.md                # This file
├── frontend/                # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   │   ├── common/      # Layout, Sidebar, Button, etc.
│   │   │   ├── chat/        # Chat-specific components
│   │   │   ├── agents/      # Agent management components
│   │   │   ├── skills/      # Skill management components
│   │   │   └── mcp/         # MCP management components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API service functions
│   │   ├── types/           # TypeScript type definitions
│   │   └── utils/           # Utility functions
│   ├── package.json
│   └── vite.config.ts
└── backend/                 # FastAPI backend application
    ├── main.py              # Application entry point
    ├── config.py            # Configuration settings
    ├── routers/             # API route handlers
    │   ├── agents.py        # Agent CRUD endpoints
    │   ├── skills.py        # Skill CRUD endpoints
    │   ├── mcp.py           # MCP CRUD endpoints
    │   └── chat.py          # Chat streaming endpoint
    ├── core/                # Business logic
    │   ├── agent_manager.py # Agent lifecycle management
    │   └── session_manager.py # Session management
    ├── database/            # Database layer
    │   └── mock_db.py       # In-memory mock database
    ├── schemas/             # Pydantic models
    └── requirements.txt
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.12+
- uv (Python package manager, recommended) or pip
- ANTHROPIC_API_KEY environment variable

### Quick Start (Recommended)

The easiest way to run the platform is using the provided scripts:

```bash
# Start both backend and frontend
./start.sh

# Stop both services
./stop.sh
```

The `start.sh` script will:
- Check and install dependencies if needed
- Create `.env` file from `.env.example` if it doesn't exist
- Start backend on http://localhost:8000
- Start frontend on http://localhost:5173
- Show logs locations and status

**Important**: After running `./start.sh` for the first time, edit `backend/.env` and add your `ANTHROPIC_API_KEY`.

### Manual Setup

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173

#### Backend Setup

```bash
cd backend

# Create virtual environment (using uv)
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate


# Create .env file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Start the server
python main.py
# Or with uvicorn directly:
# uvicorn main:app --reload --port 8000
```

The backend API will be available at http://localhost:8000

API documentation: http://localhost:8000/docs

### Running Both Services Manually

For development, run both services:

1. Terminal 1 (Backend):
   ```bash
   cd backend && python main.py
   ```

2. Terminal 2 (Frontend):
   ```bash
   cd frontend && npm run dev
   ```

The frontend is configured to proxy `/api` requests to the backend.

### Viewing Logs

When running with `./start.sh`, logs are stored in the `logs/` directory:

```bash
# View backend logs
tail -f logs/backend.log

# View frontend logs
tail -f logs/frontend.log
```

## Features

### Chat Interface
- Real-time streaming responses via SSE
- Message history sidebar
- Tool call visualization
- Enable/disable Skills and MCP toggles

### Agent Management
- Create, edit, and delete agents
- Configure model, max tokens, and permissions
- Assign skills and MCP servers to agents
- Toggle agent status (active/inactive)

### Skill Management
- List and search skills
- Upload skill packages (ZIP)
- AI-generated skill creation
- Delete custom skills

### MCP Server Management
- List and search MCP servers
- Add new MCP server configurations
- Support for stdio, SSE, and HTTP connection types
- Connection status monitoring
- Test connections

## API Endpoints

### Agents
- `GET /api/agents` - List all agents
- `GET /api/agents/{id}` - Get agent by ID
- `POST /api/agents` - Create agent
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent

### Skills
- `GET /api/skills` - List all skills
- `POST /api/skills/upload` - Upload skill ZIP
- `POST /api/skills/generate` - AI-generate skill
- `DELETE /api/skills/{id}` - Delete skill

### MCP Servers
- `GET /api/mcp` - List all MCP servers
- `POST /api/mcp` - Create MCP server
- `PUT /api/mcp/{id}` - Update MCP server
- `DELETE /api/mcp/{id}` - Delete MCP server
- `POST /api/mcp/{id}/test` - Test connection

### Chat
- `POST /api/chat/stream` - Stream chat (SSE)
- `GET /api/chat/sessions` - List sessions
- `DELETE /api/chat/sessions/{id}` - Delete session

## Configuration

### Environment Variables

The backend supports several configuration options via environment variables in `backend/.env`:

#### Required
- `ANTHROPIC_API_KEY` - Your Anthropic API key (required)

#### Optional - Claude API Configuration
- `ANTHROPIC_BASE_URL` - Custom API endpoint URL (for proxies or custom endpoints)
- `CLAUDE_CODE_USE_BEDROCK` - Set to `true` to use AWS Bedrock instead of Anthropic API
- `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` - Set to `true` to disable experimental features
- `DEFAULT_MODEL` - Default Claude model (default: `claude-sonnet-4-5-20250929`)

#### Optional - Server Configuration
- `DEBUG` - Enable debug mode (default: `true`)
- `HOST` - Server host (default: `0.0.0.0`)
- `PORT` - Server port (default: `8000`)

See `backend/.env.example` for a complete configuration template.

## Design System

The UI follows a consistent dark theme design:

- **Primary Color**: `#2b6cee` (blue)
- **Background**: `#101622` (dark)
- **Card Background**: `#1a1f2e`
- **Font**: Space Grotesk
- **Icons**: Material Symbols Outlined

## Development

### Frontend Commands

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run test         # Run tests
```

### Backend Commands

```bash
python main.py       # Start with auto-reload
uvicorn main:app --reload  # Alternative startup
```

## Architecture

For detailed architecture documentation, see [ARCHITECTURE.md](./ARCHITECTURE.md).

For development plan and roadmap, see [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md).

## License

MIT License
