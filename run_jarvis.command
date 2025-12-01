#!/bin/bash

# === CHANGE THIS TO YOUR REAL PROJECT PATH ===
PROJECT_DIR="/Users/rajaryan/Desktop/PYTHON/JARVIS project"

cd "$PROJECT_DIR" || exit 1

# If you use a venv, activate it
if [ -f ".venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
elif [ -f "jarvis_env/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "jarvis_env/bin/activate"
fi

# Start Flask server in background
python3 server.py &

# Give server a moment to start
sleep 2

# Open Chrome to the HUD
open -a "Google Chrome" "http://127.0.0.1:5001"

# Wait for server process
wait
