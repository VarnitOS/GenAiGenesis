#!/bin/bash

# Script to restart the GenAI Genesis backend service

echo "🔄 Restarting GenAI Genesis Backend Service"
echo "=========================================="

# Get the current directory of the script and navigate to backend folder
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

# Change to backend directory
cd "$BACKEND_DIR" || { echo "❌ Could not navigate to backend directory"; exit 1; }
echo "📂 Working directory: $(pwd)"

# Kill existing Flask processes
echo "🛑 Stopping existing Flask processes..."
pkill -f "python app.py" || echo "No existing processes found"

# Activate virtual environment (if it exists)
if [ -d "venv" ]; then
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies (optional)
echo "📦 Checking dependencies..."
pip install -r requirements.txt > /dev/null

# Check if SerpAPI key is set
if grep -q "SERPAPI_KEY=your_serpapi_key_here" .env; then
    echo "⚠️  Warning: You need to replace SERPAPI_KEY in .env with a real key"
    echo "   Get a key from: https://serpapi.com/"
fi

# Start the Flask application
echo "🚀 Starting Flask application..."
python app.py 