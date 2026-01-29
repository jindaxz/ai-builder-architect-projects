#!/usr/bin/env bash
set -euo pipefail

# Start the API server
# Usage: ./scripts/start_server.sh [port]

PORT="${1:-8810}"

echo "Starting image analysis API server on port $PORT..."
echo "API docs will be available at: http://127.0.0.1:$PORT/docs"
echo "Press CTRL+C to stop the server"
echo ""

cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || {
    echo "Error: Virtual environment not found. Please run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
}

uvicorn app.main:app --host 127.0.0.1 --port "$PORT" --reload --app-dir src
