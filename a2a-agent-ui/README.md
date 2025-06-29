# A2A Demo UI

A beautiful user interface for managing and invoking remote agents using the A2A (Agent-to-Agent) protocol, built with Next.js and Cloudscape Design.

## Features

- **Agent Management**: Add, list, and delete remote agents
- **Beautiful UI**: Built with AWS Cloudscape Design components
- **Real-time Communication**: Stream responses from remote agents using SSE
- **Multi-agent Support**: Invoke multiple agents simultaneously
- **Responsive Design**: Works on desktop and mobile devices

## Architecture

- **Frontend**: Next.js 14 with TypeScript and Cloudscape Design
- **Backend**: FastAPI with A2A protocol support
- **Communication**: RESTful API with Server-Sent Events (SSE) for streaming

## Prerequisites

- Node.js 18+
- Python 3.13+
- uv (Python package manager)
- A2A SDK and Strands agents dependencies

## Installation

1. **Install Frontend Dependencies**
   ```bash
   npm install
   ```

2. **Install Backend Dependencies**
   ```bash
   cd backend
   uv sync
   ```

## Configuration

1. **Backend Configuration**
   - The FastAPI server will run on port 8000
   - CORS is configured to allow frontend access
   - The frontend uses Next.js API routes to proxy requests to the backend

2. **Environment Variables** (Optional)
   - Set `BACKEND_URL` environment variable if backend runs on a different URL
   - Default backend URL is `http://localhost:8000`

## Running the Application

### Option 1: Use the Start Script (Recommended)
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual Start
1. **Start Backend Server**
   ```bash
   cd backend
   uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Frontend Server** (in another terminal)
   ```bash
   npm run dev
   ```

## Usage

1. **Access the UI**: Open http://localhost:3000
2. **Add Remote Agents**: Use the "Add Agent" functionality to register agents by URL
3. **View Agents**: See all registered agents in the table with their details
4. **Invoke Agents**: Select agents and send queries with streaming responses

## API Endpoints

The backend provides the following REST API endpoints:

- `GET /list_agents` - List all registered remote agents
- `POST /add_agent` - Register a new remote agent by URL
- `DELETE /delete_agent` - Remove a registered agent
- `POST /invoke_stream` - Invoke agents with streaming SSE response
- `GET /health` - Health check endpoint

## Project Structure

```
a2a-demo-ui/
├── src/
│   ├── app/
│   │   ├── api/            # Next.js API routes (proxy to backend)
│   │   │   ├── list_agents/
│   │   │   ├── add_agent/
│   │   │   ├── delete_agent/
│   │   │   ├── update_agent_enabled/
│   │   │   └── invoke_stream/
│   │   ├── chat/           # Chat page
│   │   └── page.tsx        # Home page
│   ├── components/         # React components
│   ├── services/          # API service layer
│   └── types/             # TypeScript type definitions
├── backend/
│   ├── main.py            # FastAPI application
│   └── pyproject.toml     # Python dependencies
├── public/                # Static assets
└── README.md
```

## Development

- Frontend runs on http://localhost:3000
- Backend API runs on http://localhost:8000
- API documentation available at http://localhost:8000/docs

## Technologies Used

- **Frontend**: Next.js 14, TypeScript, Cloudscape Design
- **Backend**: FastAPI, Python, A2A SDK
- **Communication**: REST API, Server-Sent Events (SSE)
- **Styling**: Cloudscape Design System

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
