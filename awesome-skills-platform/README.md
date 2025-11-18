# Agent Platform

A full-stack AI agent management platform built with React, FastAPI, and DynamoDB.

## Architecture

```
Frontend (React + Vite)     Backend (FastAPI)      Database (DynamoDB)
    Port: 5173        <-->    Port: 8000      <-->    AWS Region: us-east-1
                      Proxy
```

## Features

- **Agent Management**: Create, configure, and monitor AI agents
- **Skills Library**: Manage reusable agent skills
- **MCP Server Integration**: Connect to Model Context Protocol servers
- **Real-time Updates**: Live data synchronization with TanStack Query
- **Secure API Access**: Frontend proxy prevents direct API exposure

## Tech Stack

### Frontend
- React 19 + TypeScript
- Vite for build and development
- TanStack Query for data fetching and caching
- Axios for HTTP requests
- Tailwind CSS v4 for styling
- React Router v6 for navigation

### Backend
- FastAPI for REST API
- boto3 for AWS DynamoDB integration
- Pydantic for data validation
- uvicorn as ASGI server

### Database
- AWS DynamoDB (PAY_PER_REQUEST billing)
- 3 tables: agents, skills, mcp-servers

## Getting Started

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.12+ (for backend)
- AWS credentials configured (for DynamoDB)

### Backend Setup

1. Create DynamoDB tables:
```bash
python scripts/create_dynamodb_tables.py
```

2. Start the FastAPI server:
```bash
./run_api.sh
# or
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- http://localhost:8000
- API docs: http://localhost:8000/docs

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

Frontend will be available at: http://localhost:5173

## API Proxy Configuration

The frontend uses Vite's proxy feature to forward API requests to the backend. This prevents the backend API from being directly exposed to clients.

**Configuration** (in `frontend/vite.config.ts`):
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
    },
  },
}
```

**Benefits**:
- Backend API not exposed directly to clients
- Avoids CORS issues during development
- Easy to configure different backend URLs for different environments

**For Production**: Set the `VITE_API_URL` environment variable to your production API URL.

## Project Structure

```
.
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components (routes)
│   │   ├── services/        # API service layer
│   │   ├── lib/             # Utilities and configurations
│   │   └── types/           # TypeScript type definitions
│   └── vite.config.ts       # Vite configuration with proxy
├── src/                     # Backend Python application
│   ├── api/
│   │   ├── routers/         # API route handlers
│   │   └── main.py          # FastAPI application
│   ├── core/                # Core configurations
│   ├── database/            # DynamoDB client
│   └── schemas/             # Pydantic models
├── scripts/                 # Utility scripts
└── .env                     # Environment variables
```

## API Endpoints

### Agents
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create a new agent
- `GET /api/agents/{id}` - Get agent by ID
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent

### Skills
- `GET /api/skills` - List all skills
- `POST /api/skills` - Create a new skill
- `GET /api/skills/{id}` - Get skill by ID
- `DELETE /api/skills/{id}` - Delete skill

### MCP Servers
- `GET /api/mcp` - List all MCP servers
- `POST /api/mcp` - Create a new MCP server
- `GET /api/mcp/{id}` - Get MCP server by ID
- `PUT /api/mcp/{id}` - Update MCP server
- `DELETE /api/mcp/{id}` - Delete MCP server

## Environment Variables

### Backend (.env)
```bash
AWS_REGION=us-east-1
AGENTS_TABLE_NAME=agent-platform-agents
SKILLS_TABLE_NAME=agent-platform-skills
MCP_TABLE_NAME=agent-platform-mcp-servers
```

### Frontend (frontend/.env)
```bash
# Leave empty to use Vite proxy (recommended for development)
VITE_API_URL=
```

## Development Workflow

1. Start backend API server (port 8000)
2. Start frontend dev server (port 5173)
3. Frontend automatically proxies `/api/*` requests to backend
4. Changes to code trigger hot module replacement (HMR)

## License

MIT
