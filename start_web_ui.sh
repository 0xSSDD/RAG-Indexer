#!/bin/bash
# start_web_ui.sh - Launch the Streamlit web interface

set -e

echo "========================================="
echo "Starting Elixir AI Web Interface"
echo "========================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo ""
    echo "⚠️  Virtual environment not activated!"
    echo ""
    echo "Please activate it first:"
    echo "  source venv/bin/activate"
    echo ""
    exit 1
fi

# Check if indexed
if [ ! -d "qdrant_data" ]; then
    echo ""
    echo "⚠️  No index found!"
    echo ""
    echo "Please index your code first:"
    echo "  python index_hub88.py"
    echo ""
    exit 1
fi

# Check if Ollama is running (unless using Claude)
if [ "$USE_CLAUDE" != "true" ]; then
    if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
        echo ""
        echo "⚠️  Ollama not running!"
        echo ""
        echo "Start Ollama in another terminal:"
        echo "  ollama serve"
        echo ""
        echo "Or use Claude API instead:"
        echo "  export USE_CLAUDE=true"
        echo "  export ANTHROPIC_API_KEY='your-key'"
        echo ""
        exit 1
    fi
fi

echo ""
echo "✓ All checks passed!"
echo ""
echo "🚀 Launching web interface..."
echo ""
echo "The app will open in your browser at:"
echo "  http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Launch Streamlit
streamlit run web_ui.py
