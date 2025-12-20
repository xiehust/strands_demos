#!/bin/bash

# Restart script for AI Agent Platform
# Stops and then starts both services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 Restarting AI Agent Platform..."
echo ""

# Stop services
./stop.sh

echo ""
echo "⏳ Waiting 2 seconds before restart..."
sleep 2
echo ""

# Start services
./start.sh
