#!/bin/bash

# Status script for AI Agent Platform
# Shows current status of backend and frontend services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📊 AI Agent Platform Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to check service status
check_service() {
    local SERVICE=$1
    local PORT=$2
    local PID_FILE=".pids/${SERVICE}.pid"
    local URL=$3

    echo "🔍 ${SERVICE} Service:"

    # Check PID file
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "   ✅ Process running (PID: $PID)"

            # Check if service is responding
            if curl -s "$URL" > /dev/null 2>&1; then
                echo "   ✅ Service responding at $URL"
            else
                echo "   ⚠️  Process running but not responding at $URL"
            fi
        else
            echo "   ❌ PID file exists but process not running"
            echo "   💡 Run: ./stop.sh && ./start.sh"
        fi
    else
        echo "   ❌ Not running (no PID file)"
        echo "   💡 Run: ./start.sh"
    fi

    # Check port
    if lsof -ti:$PORT > /dev/null 2>&1; then
        PORT_PID=$(lsof -ti:$PORT)
        echo "   📍 Port $PORT in use by PID: $PORT_PID"
    else
        echo "   📍 Port $PORT is free"
    fi

    echo ""
}

# Check backend
check_service "backend" 8000 "http://localhost:8000/health"

# Check frontend
check_service "frontend" 5173 "http://localhost:5173"

# Show log files
echo "📝 Log Files:"
if [ -d "logs" ]; then
    if [ -f "logs/backend.log" ]; then
        BACKEND_SIZE=$(du -h logs/backend.log | cut -f1)
        BACKEND_LINES=$(wc -l < logs/backend.log)
        echo "   Backend:  logs/backend.log ($BACKEND_SIZE, $BACKEND_LINES lines)"
    fi
    if [ -f "logs/frontend.log" ]; then
        FRONTEND_SIZE=$(du -h logs/frontend.log | cut -f1)
        FRONTEND_LINES=$(wc -l < logs/frontend.log)
        echo "   Frontend: logs/frontend.log ($FRONTEND_SIZE, $FRONTEND_LINES lines)"
    fi
else
    echo "   No logs directory found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🛠️  Quick Commands:"
echo "   ./start.sh              - Start services"
echo "   ./stop.sh               - Stop services"
echo "   tail -f logs/*.log      - View logs"
echo "   ./status.sh             - Show this status"
echo ""
