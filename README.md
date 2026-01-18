# Elixir AI System: RAG for Hub88 Codebase

**AI-powered code assistant for your Elixir codebase using Retrieval Augmented Generation (RAG)**

Ask questions about your Hub88 code and get answers based on your actual implementation!

---

## 🎯 What This Does

This system lets you:
- **Ask natural language questions** about your Elixir codebase
- **Get code examples** from your actual repositories
- **Understand patterns** used in your projects
- **Find implementations** quickly without manual searching

**Example:**
```
Q: How do we handle permissions in Hub88?
A: [Shows actual permission code from your repos with explanation]
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Your Question  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Embeddings     │─────▶│  Vector Search   │
│  (Semantic)     │      │  (Qdrant)        │
└─────────────────┘      └────────┬─────────┘
                                  │
                         Retrieve relevant code
                                  │
                                  ▼
                         ┌────────────────┐
                         │  LLM           │
                         │  (Codestral/   │
                         │   Claude)      │
                         └────────┬───────┘
                                  │
                                  ▼
                         ┌────────────────┐
                         │  Answer with   │
                         │  Code Examples │
                         └────────────────┘
```

**Components:**
1. **Code Chunker** - Intelligently splits Elixir code into semantic chunks
2. **Embeddings** - Converts code to vectors (using Jina Code or MiniLM)
3. **Vector Database** - Stores and searches code (Qdrant)
4. **RAG System** - Retrieves context and generates answers (using Codestral or Claude)

---

## 🌐 Two Ways to Use

### Option 1: Web Interface (Recommended) 🎨

Beautiful ChatGPT-like interface in your browser:

```bash
./start_web_ui.sh
```

Opens at `http://localhost:8501` with:
- Chat interface
- Example questions
- Model selection
- Real-time stats

See [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) for details.

### Option 2: Command Line 💻

Traditional terminal interface:

```bash
python query_hub88.py
```

Best for automation and scripts.

---

## 📋 Prerequisites

### What Runs Where?

**THIS RUNS 100% LOCALLY ON YOUR MACHINE**

- ✅ Your code stays on your machine
- ✅ Vector database is local (Qdrant embedded mode)
- ✅ Embeddings are local (sentence-transformers)
- ⚠️ LLM can be local (Ollama) OR cloud (Claude API)

### System Requirements

**Minimum:**
- Python 3.9+
- 8GB RAM
- 5GB free disk space

**Recommended:**
- 16GB RAM (for larger codebases)
- SSD for faster indexing

**Operating System:**
- ✅ macOS (M1/M2/Intel)
- ✅ Linux (Ubuntu, Debian, etc.)
- ✅ Windows (via WSL2 recommended)

### Software Dependencies

1. **Python 3.9+**
   ```bash
   python --version  # Should be 3.9 or higher
   ```

2. **Ollama** (for local LLM - recommended)
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl https://ollama.ai/install.sh | sh
   
   # Or download from: https://ollama.ai
   ```

3. **OR Claude API** (cloud-based alternative)
   - Sign up at: https://console.anthropic.com
   - Get API key
   - Set: `export ANTHROPIC_API_KEY='your-key'`

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install

```bash
# Clone or download this directory
cd elixir-ai-system

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start Ollama (if using local LLM)

```bash
# Terminal 1: Start Ollama server
ollama serve

# Terminal 2: Pull Codestral model (one time, ~4GB download)
ollama pull codestral

# Alternative models (optional):
# ollama pull deepseek-coder  # Smaller, faster
# ollama pull llama3           # General purpose
```

### Step 3: Index Your Code

Edit `index_hub88.py` and add your repository paths:

```python
repos = [
    "/Users/arpan/hub88/backend",
    "/Users/arpan/hub88/schemas",
    # Add all your Elixir repos
]
```

Then run:

```bash
python index_hub88.py
```

**What happens:**
- Finds all `.ex` and `.exs` files
- Chunks code intelligently (preserves modules/functions)
- Generates embeddings (semantic vectors)
- Stores in Qdrant (local database)
- Takes: ~5-15 minutes for typical codebase

**Output:**
```
✓ Created 1,247 chunks from hub88_backend
✓ Indexed 1,247 chunks
✅ INDEXING COMPLETE!
```

### Step 4: Ask Questions!

```bash
python query_hub88.py
```

```
🤔 Question: How do we handle permissions in Hub88?

🔍 Query: How do we handle permissions in Hub88?
✓ Retrieved 5 relevant chunks

📝 Answer:
Hub88 handles permissions using a scope-based system...
[Shows actual code from your repos]
```

---

## 💻 Detailed Usage

### Indexing Options

**Basic indexing:**
```bash
python index_hub88.py
```

**Environment variable approach:**
```bash
export HUB88_REPOS="/path/to/repo1:/path/to/repo2"
python index_hub88.py
```

**Re-indexing (after code changes):**
```bash
# Just run indexing again - it will replace the old index
python index_hub88.py
```

### Querying Options

**With Ollama (local):**
```bash
# Default: uses Codestral
python query_hub88.py

# Use different model
export OLLAMA_MODEL="deepseek-coder"
python query_hub88.py
```

**With Claude API (cloud):**
```bash
export ANTHROPIC_API_KEY="your-key"
export USE_CLAUDE="true"
python query_hub88.py
```

### Programmatic Usage

```python
from rag_system import ElixirRAG
from embeddings import HybridCodeEmbedder
from vector_db import CodeVectorDB

# Load indexed codebase
embedder = HybridCodeEmbedder()
db = CodeVectorDB(collection_name="hub88_code")

# Initialize RAG
rag = ElixirRAG(
    vector_db=db,
    embedder=embedder,
    model="codestral",
    use_claude=False
)

# Ask questions
answer = rag.query("How do we handle authentication?")
print(answer)
```

---

## 🎓 Example Questions

**General Patterns:**
- "How do we handle errors in Hub88?"
- "What's the pattern for database queries?"
- "Show me how to create a new GenServer"

**Specific Features:**
- "How is user authentication implemented?"
- "How do we handle permissions?"
- "What's the structure of game provider integrations?"

**Code Examples:**
- "Show me an example of a Phoenix controller"
- "How do we use Ecto schemas?"
- "What's a typical supervisor tree in our app?"

**Best Practices:**
- "What naming conventions do we use?"
- "How should I structure a new module?"
- "What's our pattern for handling API requests?"

---

## 🔧 Configuration

### Chunking Parameters

Edit `code_chunker.py`:

```python
chunker = ElixirCodeChunker(
    max_chunk_size=1000,  # Max chars per chunk
    overlap=200           # Overlap between chunks
)
```

**Guidelines:**
- Smaller chunks (500-800): Better for specific code snippets
- Larger chunks (1000-1500): Better for understanding context
- More overlap (300-400): Better retrieval, uses more storage

### Embedding Models

Edit `embeddings.py`:

```python
# Use specific model
embedder = HybridCodeEmbedder(
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # Faster, smaller
    # OR
    model_name="jinaai/jina-embeddings-v2-base-code"     # Better for code
)
```

**Available models:**
- `jinaai/jina-embeddings-v2-base-code` (768 dims) - Best for code
- `sentence-transformers/all-MiniLM-L6-v2` (384 dims) - Fastest
- `BAAI/bge-large-en-v1.5` (1024 dims) - High quality

### Search Parameters

Edit `rag_system.py`:

```python
context = self.retrieve_context(
    query=question,
    k=5,              # Number of chunks to retrieve (3-10)
    repo_filter=None, # Filter by repo name (optional)
    rerank=True       # Re-rank results (recommended)
)
```

---

## 📊 Performance & Costs

### Indexing Performance

| Codebase Size | Files | Chunks | Time | Disk Space |
|--------------|-------|--------|------|------------|
| Small        | 100   | 500    | 2min | 50MB       |
| Medium       | 500   | 2,500  | 10min| 250MB      |
| Large        | 2,000 | 10,000 | 40min| 1GB        |

*Tested on M1 MacBook Pro*

### Query Performance

- **Retrieval:** ~100-500ms (vector search)
- **Generation (Ollama):** 2-10 seconds
- **Generation (Claude API):** 1-3 seconds
- **Total:** 3-10 seconds per question

### Costs

**Local (Ollama):**
- Indexing: FREE (one-time)
- Queries: FREE (unlimited)
- Storage: ~100MB per 1,000 code files

**Cloud (Claude API):**
- Indexing: FREE (local)
- Queries: ~$0.01-0.05 per question
- 100 questions/day = ~$1-5/month

---

## 🐛 Troubleshooting

### "No module named 'sentence_transformers'"

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### "Ollama connection refused"

```bash
# Start Ollama server in another terminal
ollama serve

# Make sure it's running
curl http://localhost:11434
```

### "No results found"

**Possible causes:**
1. No code indexed yet → Run `python index_hub88.py`
2. Query too specific → Try broader terms
3. Score threshold too high → Edit `score_threshold` in `vector_db.py`

```python
# Lower threshold for more results
score_threshold=0.2  # Default: 0.5
```

### "Out of memory"

**For indexing:**
```python
# Process smaller batches
embeddings = embedder.encode_batch(texts, batch_size=16)  # Default: 32
```

**For queries:**
```python
# Retrieve fewer chunks
context = rag.retrieve_context(query, k=3)  # Default: 5
```

### "Model download stuck"

```bash
# Check Ollama status
ollama list

# Manually pull model
ollama pull codestral --verbose
```

---

## 📁 Project Structure

```
elixir-ai-system/
├── README.md              # This file
├── requirements.txt       # Python dependencies
│
├── code_chunker.py       # Intelligent code chunking
├── embeddings.py         # Embedding generation
├── vector_db.py          # Qdrant vector database
├── rag_system.py         # RAG system logic
│
├── index_hub88.py        # Indexing script (run once)
├── query_hub88.py        # Query interface (interactive)
│
├── qdrant_data/          # Generated: vector database
└── index_metadata.json   # Generated: indexing metadata
```

---

## 🔒 Privacy & Security

**Your code stays private:**
- ✅ All code stored locally (not uploaded anywhere)
- ✅ Embeddings generated locally
- ✅ Vector database is local
- ⚠️ If using Claude API: only retrieved snippets sent (not entire codebase)
- ⚠️ If using Ollama: 100% local, nothing leaves your machine

**Recommendations:**
- Use Ollama for maximum privacy (everything local)
- Use Claude API only if comfortable with code snippets being sent
- Add `.gitignore` for `qdrant_data/` to avoid committing indexes

---

## 🚧 Known Limitations

1. **Language:** Only Elixir/Erlang (not Phoenix templates, JS, CSS)
2. **Context:** Limited to indexed code (doesn't know external dependencies)
3. **Updates:** Must re-index after significant code changes
4. **Memory:** Large codebases (10,000+ files) may need 16GB+ RAM

---

## 🗺️ Roadmap

**Next steps (for fine-tuning - Part 2):**
- [ ] Create comprehensive Elixir dataset
- [ ] Fine-tune Codestral on Elixir patterns
- [ ] Combine RAG + fine-tuned model
- [ ] Deploy as VS Code extension

---

## 🙋 FAQ

**Q: Do I need a GPU?**
A: No! CPU is fine for embeddings and Ollama. GPU helps but not required.

**Q: Can I use this for other languages?**
A: Yes! Modify `code_chunker.py` for Python, JS, etc. The system is language-agnostic.

**Q: How do I update after code changes?**
A: Just re-run `python index_hub88.py`. It replaces the old index.

**Q: Can I deploy this for my team?**
A: Yes! Host Qdrant on a server and point clients to it. See Qdrant docs.

**Q: Does this work offline?**
A: With Ollama: YES (100% offline). With Claude: NO (needs internet).

---

## 📞 Support

**Issues with this system:**
- Check troubleshooting section above
- Verify all dependencies installed
- Check Ollama is running (`ollama list`)

**Questions about Elixir code:**
- Ask the system! That's what it's for 😊

---

## ✅ Next: Fine-Tuning (Part 2)

This RAG system is **Part 1** - it works with existing models.

**Part 2** will cover:
- Creating a comprehensive Elixir dataset
- Fine-tuning Codestral on Elixir patterns
- Combining RAG + fine-tuned model for best results
- Building the "FunctionalCode-1.0" dataset for the community

Ready to continue with Part 2? Let me know!

---

**Built with ❤️ for the Elixir community**
