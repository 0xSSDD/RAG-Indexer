#!/bin/bash
# start_web_ui.sh - Simple launcher for web UI

set -e

echo "🧪 Starting Elixir AI Web Interface..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  No virtual environment found!"
    echo ""
    echo "Run setup first:"
    echo "  ./setup.sh"
    echo ""
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Install streamlit if not installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing Streamlit..."
    pip install streamlit==1.31.0 requests -q
    echo "✓ Streamlit installed"
    echo ""
fi

echo "🚀 Launching web interface..."
echo ""
echo "Opening at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Launch
streamlit run web_ui.py --server.headless true
