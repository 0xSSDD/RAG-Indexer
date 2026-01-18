# Where Does This Run? (Deployment Guide)

## TL;DR

**THIS RUNS 100% LOCALLY ON YOUR MACHINE**

- ✅ Your code: Never leaves your computer
- ✅ Vector database: Stored locally
- ✅ Embeddings: Generated locally
- ⚠️ LLM: Can be local (Ollama) OR cloud (Claude API)

---

## Architecture: Local vs Cloud

```
┌────────────────────────────────────────────────────────┐
│           YOUR COMPUTER (100% Local)                   │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐     ┌──────────────┐                │
│  │  Your Code   │────▶│ Code Chunker │                │
│  │  (Hub88)     │     │  (Python)    │                │
│  └──────────────┘     └──────┬───────┘                │
│                               │                         │
│                               ▼                         │
│                      ┌──────────────┐                  │
│                      │  Embeddings  │                  │
│                      │  (sentence-  │                  │
│                      │  transformers)│                 │
│                      └──────┬───────┘                  │
│                               │                         │
│                               ▼                         │
│                      ┌──────────────┐                  │
│                      │   Qdrant     │                  │
│                      │   Database   │                  │
│                      │   (Local)    │                  │
│                      └──────┬───────┘                  │
│                               │                         │
│         ┌─────────────────────┼─────────────┐          │
│         │                     │             │          │
│         ▼                     ▼             ▼          │
│  ┌──────────┐         ┌──────────┐   ┌──────────┐    │
│  │ Ollama   │         │  OR      │   │ Claude   │────┼──▶ Internet
│  │ (Local)  │         │          │   │ API      │    │   (Cloud)
│  │ Codestral│         │          │   │ (Cloud)  │    │
│  └──────────┘         └──────────┘   └──────────┘    │
│      ▲                                      ▲          │
│      │                                      │          │
│      └──────────────┬───────────────────────┘          │
│                     │                                   │
│              ┌──────────────┐                          │
│              │   Answer     │                          │
│              └──────────────┘                          │
│                                                         │
└────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Code Chunker (100% Local)
- **Where:** Your computer
- **What:** Splits your Elixir code into chunks
- **Privacy:** Your code never leaves your machine
- **Storage:** Temporary, in memory

### 2. Embeddings (100% Local)
- **Where:** Your computer
- **What:** Converts code to vectors using sentence-transformers
- **Model:** Downloaded once, runs locally
- **Privacy:** No data sent anywhere
- **Size:** ~500MB for model files

### 3. Vector Database - Qdrant (100% Local)
- **Where:** Your computer in `./qdrant_data/`
- **What:** Stores code embeddings for search
- **Privacy:** All data local
- **Size:** ~100MB per 1,000 code chunks
- **Alternative:** Can host on server for team access (optional)

### 4. LLM - Two Options

#### Option A: Ollama (100% Local) ✅ RECOMMENDED
- **Where:** Your computer
- **What:** Runs Codestral/other models locally
- **Privacy:** Nothing leaves your machine
- **Requirements:** 
  - 8GB RAM minimum
  - 4-8GB disk for model
  - Works offline
- **Speed:** 2-10 seconds per query
- **Cost:** FREE

#### Option B: Claude API (Cloud) ⚠️
- **Where:** Anthropic's servers
- **What:** Sends retrieved code snippets to Claude
- **Privacy:** Only relevant snippets sent, not entire codebase
- **Requirements:**
  - API key
  - Internet connection
- **Speed:** 1-3 seconds per query
- **Cost:** ~$0.01-0.05 per question

---

## Privacy Comparison

### With Ollama (Fully Local)
```
Your Code → Stays on your computer
Embeddings → Generated on your computer
Database → Stored on your computer
LLM → Runs on your computer
Result → All local, zero cloud
```

**Privacy Level:** 🔒🔒🔒🔒🔒 (Maximum)

### With Claude API (Hybrid)
```
Your Code → Stays on your computer
Embeddings → Generated on your computer
Database → Stored on your computer
LLM → Retrieved snippets sent to Claude
Result → Answer comes from cloud
```

**Privacy Level:** 🔒🔒🔒 (Good - only snippets sent)

---

## What Actually Gets Sent to the Cloud?

### With Ollama: NOTHING ✅
- 100% offline capable
- All processing local
- No telemetry, no phone home

### With Claude API: ONLY RELEVANT SNIPPETS
**Example query:** "How do we handle permissions?"

**What Claude API sees:**
```elixir
# Relevant code snippet 1 (~200 lines)
defmodule Hub88.Auth.Permissions do
  # ... your code ...
end

# Relevant code snippet 2 (~200 lines)
# ... more relevant code ...
```

**What Claude API does NOT see:**
- Your entire codebase
- Unrelated code
- Your file structure
- Your secrets/credentials
- Your database

**Total sent:** ~3-5 code snippets per query (~1KB of code)

---

## System Requirements

### Minimum (Works but Slow)
- **CPU:** Dual-core
- **RAM:** 8GB
- **Disk:** 10GB free
- **OS:** macOS, Linux, or Windows (WSL2)

### Recommended (Smooth Experience)
- **CPU:** Quad-core or better
- **RAM:** 16GB
- **Disk:** 20GB free (SSD preferred)
- **OS:** macOS M1/M2 or modern Linux

### For Large Codebases (10,000+ files)
- **RAM:** 32GB
- **Disk:** 50GB free SSD
- **CPU:** 8+ cores helps with indexing

---

## Deployment Scenarios

### 1. Personal Use (You Only)
**Setup:** Everything local on your laptop

```
Your Laptop:
├── Code repositories (Hub88)
├── Python + dependencies
├── Qdrant database (local)
├── Ollama + Codestral
└── Query interface
```

**Pros:** Maximum privacy, works offline, free
**Cons:** Not shared with team

---

### 2. Team Use (Shared Database)
**Setup:** Qdrant on server, everyone connects

```
Team Member 1:                   Central Server:
├── Query interface              ├── Qdrant (hosted)
└── Connects to server ────────▶ ├── All team's code indexes
                                 └── Shared embeddings

Team Member 2:
├── Query interface
└── Connects to server ────────▶ (Same server)
```

**How to do this:**
1. Host Qdrant on a server (Docker)
2. Index all team repos once
3. Team members query remotely

**Pros:** Team shares knowledge, one index
**Cons:** Requires server, code leaves local machine

**Qdrant hosting options:**
- Self-hosted (Docker): FREE
- Qdrant Cloud: ~$25/month
- AWS/GCP/Azure: ~$20-50/month

---

### 3. Hybrid (Local Index, Cloud LLM)
**Setup:** Your code indexed locally, use Claude API for answers

```
Your Laptop:
├── Code repositories (local)
├── Qdrant database (local)
├── Embeddings (local)
└── Claude API (cloud) ────────▶ Anthropic Servers
                                 (only gets snippets)
```

**Pros:** Faster responses, good quality
**Cons:** API costs, snippets sent to cloud

---

## Can This Run On...?

### ✅ Your Laptop (macOS/Linux/Windows)
**Yes!** This is the primary use case.

### ✅ Your Desktop
**Yes!** Even better with more resources.

### ✅ A Server (for team)
**Yes!** Host Qdrant, team connects.

### ✅ Docker Container
**Yes!** Can containerize entire system.

### ✅ Cloud VM (AWS/GCP/Azure)
**Yes!** But why? Better to run local.

### ❌ Browser (JavaScript)
**No.** Needs Python + ML libraries.

### ❌ Mobile Phone
**No.** Too resource-intensive.

---

## Internet Requirements

### For Ollama (Local LLM):
**During setup:**
- Download Ollama: ~100MB
- Download Codestral model: ~4GB
- Download Python packages: ~2GB

**After setup:**
- ✅ Can work 100% offline
- ✅ No internet needed for queries
- ✅ Perfect for airplanes, secure networks

### For Claude API:
**Always requires internet:**
- Queries sent to Anthropic servers
- ~1KB per query
- Works on slow connections

---

## Security Considerations

### Secrets in Code
**Your code may contain:**
- API keys
- Database passwords
- Internal URLs

**What happens:**
- With Ollama: Stays local, secure ✅
- With Claude: Could be in snippets sent ⚠️

**Recommendation:**
- Use Ollama for maximum security
- Or sanitize code before indexing
- Never index `.env` files

### Compliance
**For regulated industries:**
- Healthcare (HIPAA): Use Ollama only
- Finance (SOX): Use Ollama only
- Defense: Use Ollama only, air-gapped machine

---

## Cost Breakdown

### One-Time Costs
- Setup time: 30 minutes (your time)
- Learning curve: 1 hour
- Initial indexing: 15 minutes

### Ongoing Costs (Ollama)
- Electricity: ~$0.01/day
- Disk space: ~100MB per repo
- Maintenance: Re-index monthly (~15 min)
- **Total: FREE**

### Ongoing Costs (Claude API)
- Per query: $0.01-0.05
- 100 queries/day: ~$1-5/month
- Still need local storage/compute

---

## Recommended Setup

**For maximum privacy + zero cost:**
```bash
# 1. Install Ollama
brew install ollama

# 2. Pull Codestral
ollama pull codestral

# 3. Index your code locally
python index_hub88.py

# 4. Query (all local)
python query_hub88.py
```

**Result:**
- ✅ Zero cloud dependencies
- ✅ Works offline
- ✅ Free forever
- ✅ Maximum privacy

---

## Summary

**Where does this run?**
- **Your code:** Your computer only
- **Chunking:** Your computer
- **Embeddings:** Your computer
- **Database:** Your computer (or team server)
- **LLM:** Your choice (local or cloud)

**Default setup: 100% local with Ollama**

**Best for Hub88:** Local with Ollama, expand to team server later if needed.

---

Questions? Check README.md or ask the system itself! 😊
