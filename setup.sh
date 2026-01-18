#!/bin/bash
# setup.sh - Automated setup for Elixir AI System

set -e  # Exit on error

echo "========================================="
echo "Elixir AI System - Setup"
echo "========================================="

# Check Python version
echo ""
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Created venv/"
else
    echo "✓ venv/ already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Install Ollama (if not already installed):"
echo "   https://ollama.ai"
echo ""
echo "3. Pull Codestral model:"
echo "   ollama pull codestral"
echo ""
echo "4. Edit index_hub88.py with your repository paths"
echo ""
echo "5. Index your code:"
echo "   python index_hub88.py"
echo ""
echo "6. Start querying:"
echo "   python query_hub88.py"
echo ""
echo "See README.md for detailed instructions."
echo ""
