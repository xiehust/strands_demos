#!/bin/bash

# Stop script for AI Agent Platform
# Stops both backend and frontend services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛑 Stopping AI Agent Platform..."

# Function to stop a service
stop_service() {
    local SERVICE=$1
    local PID_FILE=".pids/${SERVICE}.pid"

    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "🔴 Stopping ${SERVICE} (PID: $PID)..."
            kill $PID

            # Wait for process to stop
            for i in {1..10}; do
                if ! ps -p $PID > /dev/null 2>&1; then
                    echo "✅ ${SERVICE} stopped"
                    break
                fi
                if [ $i -eq 10 ]; then
                    echo "⚠️  Force killing ${SERVICE}..."
                    kill -9 $PID 2>/dev/null || true
                fi
                sleep 1
            done
        else
            echo "⚠️  ${SERVICE} process not found (PID: $PID)"
        fi
        rm "$PID_FILE"
    else
        echo "⚠️  No PID file found for ${SERVICE}"
    fi
}

# Stop backend
stop_service "backend"

# Stop frontend
stop_service "frontend"

# Also kill any remaining processes on those ports
echo "🧹 Cleaning up any remaining processes..."

# Get current shell PID and parent PID to avoid killing ourselves
CURRENT_PID=$$
PARENT_PID=$PPID

# Kill processes on port 8000 (backend), excluding current shell
for pid in $(lsof -ti:8000 2>/dev/null); do
    if [ "$pid" != "$CURRENT_PID" ] && [ "$pid" != "$PARENT_PID" ]; then
        kill -9 "$pid" 2>/dev/null || true
    fi
done

# Kill processes on port 5173 (frontend), excluding current shell
for pid in $(lsof -ti:5173 2>/dev/null); do
    if [ "$pid" != "$CURRENT_PID" ] && [ "$pid" != "$PARENT_PID" ]; then
        kill -9 "$pid" 2>/dev/null || true
    fi
done

echo ""
echo "✅ AI Agent Platform stopped successfully"
echo ""
