#!/bin/bash

# Start the FastAPI backend server
echo "Starting FastAPI backend server..."
cd backend

# Initialize uv environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Initializing uv environment..."
    uv sync
fi

# Start backend with uv
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start the Next.js frontend
echo "Starting Next.js frontend..."
cd ..
npm run dev &
FRONTEND_PID=$!

# Function to cleanup processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

echo "Both servers are running:"
echo "- Backend API: http://localhost:8000"
echo "- Frontend UI: http://localhost:3000"
echo "- API Documentation: http://localhost:8000/docs"
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait