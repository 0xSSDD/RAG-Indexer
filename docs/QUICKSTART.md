# Quick Start Guide

Get your Elixir AI assistant running in 5 minutes!

## TL;DR (Fast Track)

```bash
# 1. Setup
./setup.sh

# 2. Test installation
source venv/bin/activate
python test_installation.py

# 3. Start Ollama (in another terminal)
ollama serve

# 4. Pull model (one time)
ollama pull codestral

# 5. Edit index_hub88.py - add your repo paths
nano index_hub88.py  # or vim, or your favorite editor

# 6. Index your code
python index_hub88.py

# 7. Ask questions!
python query_hub88.py
```

## Detailed Steps

### 1. Install System Dependencies

**macOS:**
```bash
# Install Ollama
brew install ollama

# Or download from https://ollama.ai
```

**Linux:**
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh
```

**Windows:**
- Install WSL2: https://docs.microsoft.com/en-us/windows/wsl/install
- Then follow Linux instructions

### 2. Run Setup Script

```bash
cd elixir-ai-system
./setup.sh
```

This will:
- Create virtual environment
- Install all Python dependencies
- Verify installation

### 3. Test Installation

```bash
source venv/bin/activate  # Activate virtual environment
python test_installation.py
```

Expected output:
```
✅ All tests passed!
```

### 4. Configure Your Repositories

Edit `index_hub88.py`:

```python
repos = [
    "/Users/your-name/hub88/backend",
    "/Users/your-name/hub88/schemas",
    # Add all your Elixir repos here
]
```

**Tips:**
- Use absolute paths (not relative)
- Include all relevant Elixir repositories
- Can add repos one at a time and re-index

### 5. Start Ollama Server

In a **separate terminal**:

```bash
ollama serve
```

Keep this running in the background.

### 6. Pull Codestral Model

```bash
# This downloads ~4GB, takes 5-10 minutes
ollama pull codestral

# Verify it's installed
ollama list
```

**Alternative models:**
```bash
# Smaller/faster
ollama pull deepseek-coder

# General purpose
ollama pull llama3
```

### 7. Index Your Codebase

```bash
python index_hub88.py
```

**What to expect:**
- Takes 5-15 minutes for typical codebase
- Progress bars show chunking and embedding
- Creates `qdrant_data/` directory
- Creates `index_metadata.json`

**Example output:**
```
Found 543 Elixir files in hub88_backend
Created 1,247 chunks from hub88_backend
✓ Indexed 1,247 chunks
✅ INDEXING COMPLETE!
```

### 8. Start Querying!

```bash
python query_hub88.py
```

**Try these questions:**
```
How do we handle permissions?
Show me a GenServer example
What's the pattern for database queries?
```

## Troubleshooting Quick Fixes

**"Module not found"**
```bash
source venv/bin/activate  # Make sure venv is active
pip install -r requirements.txt
```

**"Ollama connection refused"**
```bash
# Make sure Ollama is running
ollama serve  # In another terminal
```

**"No results found"**
```bash
# Make sure you indexed first
python index_hub88.py
```

**"Out of memory"**
- Close other applications
- Index fewer repos at once
- Use smaller batch size (edit code)

## Usage Tips

**Better questions:**
- ✅ "How do we handle authentication in Hub88?"
- ✅ "Show me examples of GenServers"
- ✅ "What's the pattern for Ecto queries?"
- ❌ "Write me a complete app"
- ❌ "What is Elixir?" (use web search for general questions)

**Re-indexing:**
- After major code changes: re-run `python index_hub88.py`
- Small changes: no need to re-index
- Added new repo: add to list and re-run

**Performance:**
- First query: slower (loading models)
- Subsequent queries: faster
- Use `k=3` for faster queries (fewer chunks)

## What's Next?

1. **Use it daily** - Ask questions as you code
2. **Tune it** - Adjust chunk size, embedding models
3. **Share with team** - Host Qdrant on server
4. **Part 2** - Fine-tune your own model

See README.md for full documentation!

---

**Need help?** Check README.md troubleshooting section.
