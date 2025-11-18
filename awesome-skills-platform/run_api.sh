#!/bin/bash
# Script to run the FastAPI server

echo "Starting Agent Platform API..."
echo "API will be available at: http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo ""

uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
