# 🤖 Managing Ollama Models - Complete Guide

## 📋 Quick Reference

```bash
# List all models
ollama list

# Pull (download) a model
ollama pull codestral

# Remove a model
ollama rm codestral

# Show model details
ollama show codestral

# Run a model (interactive)
ollama run codestral

# Check Ollama version
ollama --version
```

---

## 📦 Listing Models

### See what you have:

```bash
ollama list
```

**Output:**
```
NAME              ID           SIZE    MODIFIED
codestral:latest  a1b2c3d4     4.1 GB  2 hours ago
deepseek-coder    e5f6g7h8     6.7 GB  3 days ago
llama3:latest     i9j0k1l2     4.7 GB  1 week ago
```

**Columns:**
- **NAME** - Model name (what you use in code)
- **ID** - Unique identifier
- **SIZE** - Disk space used
- **MODIFIED** - Last used/updated

---

## 📥 Downloading Models

### Pull a specific model:

```bash
ollama pull codestral
```

**Shows progress:**
```
pulling manifest
pulling 8934d96d3f08... 100% ▕████████████▏ 4.1 GB
pulling 8c17c2ebb0ea... 100% ▕████████████▏ 7.0 KB
pulling 7c23fb36d801... 100% ▕████████████▏ 4.8 KB
pulling 2e0493f67d0c... 100% ▕████████████▏   59 B
pulling fa304d675061... 100% ▕████████████▏   91 B
pulling 42ba7f8a01dd... 100% ▕████████████▏  557 B
verifying sha256 digest
writing manifest
removing any unused layers
success
```

### Popular models for coding:

```bash
# Best for Elixir (our default)
ollama pull codestral

# Fast & lightweight
ollama pull deepseek-coder

# General purpose, good at code
ollama pull llama3

# Smaller, faster
ollama pull mistral

# Very small, for testing
ollama pull tinyllama
```

### Pull specific version:

```bash
# Latest (default)
ollama pull codestral:latest

# Specific tag
ollama pull codestral:32k

# Specific size
ollama pull llama3:8b    # 8 billion parameters
ollama pull llama3:70b   # 70 billion parameters (huge!)
```

---

## 🗑️ Removing Models

### Delete a model:

```bash
ollama rm codestral
```

**Confirmation:**
```
deleted 'codestral'
```

### Free up space - remove unused models:

```bash
# List models first
ollama list

# Remove old ones
ollama rm old-model-1
ollama rm old-model-2
```

### Remove all versions of a model:

```bash
# This removes codestral:latest, codestral:32k, etc.
ollama rm codestral
```

---

## 📊 Model Information

### See model details:

```bash
ollama show codestral
```

**Output:**
```
Model Details:
  Format: gguf
  Family: llama
  Families: [llama]
  Parameter Size: 22.2B
  Quantization Level: Q4_0

System:
  You are a helpful AI assistant.

License:
  APACHE 2.0

Parameters:
  stop    "<|im_end|>"
  stop    "<|im_start|>"
```

---

## 💾 Where Are Models Stored?

### Default locations:

**macOS:**
```
~/.ollama/models
```

**Linux:**
```
~/.ollama/models
```

**Windows:**
```
C:\Users\<username>\.ollama\models
```

### Check disk usage:

```bash
# macOS/Linux
du -sh ~/.ollama/models

# Output
24G     /Users/you/.ollama/models
```

### See what's taking space:

```bash
# List by size
du -sh ~/.ollama/models/* | sort -hr
```

**Output:**
```
8.1G    /Users/you/.ollama/models/blobs/sha256-abc123...
6.7G    /Users/you/.ollama/models/blobs/sha256-def456...
4.1G    /Users/you/.ollama/models/blobs/sha256-ghi789...
```

---

## 🔄 Updating Models

### Update a model to latest version:

```bash
# This re-downloads if there's a newer version
ollama pull codestral
```

**Output if already latest:**
```
✓ codestral is up to date
```

**Output if update available:**
```
pulling manifest
pulling updates... 100%
success
```

### Update all models:

```bash
# Get list of models
ollama list | tail -n +2 | awk '{print $1}' | while read model; do
  echo "Updating $model..."
  ollama pull "$model"
done
```

---

## 🎯 Recommended Models by Use Case

### For Elixir Code (Our Use Case):

**Best Choice:**
```bash
ollama pull codestral       # 22B params, 4.1 GB
```
- Trained specifically for code
- Great at Elixir
- Good balance of quality/speed

**Faster Alternative:**
```bash
ollama pull deepseek-coder  # 6.7B params, 3.8 GB
```
- Faster responses
- Good at code
- Smaller size

**Lightweight:**
```bash
ollama pull mistral         # 7B params, 4.1 GB
```
- General purpose
- Decent at code
- Fast

### For General Use:

```bash
ollama pull llama3          # 8B params, 4.7 GB
```
- Best general model
- Good at everything
- Meta's flagship

---

## 📏 Model Sizes Explained

| Params | Size  | Speed    | Quality | Best For |
|--------|-------|----------|---------|----------|
| 3B     | ~2 GB | Fastest  | Basic   | Testing |
| 7B     | ~4 GB | Fast     | Good    | Daily use |
| 13B    | ~7 GB | Medium   | Great   | Complex tasks |
| 22B    | ~12GB | Slower   | Excellent| Code/analysis |
| 70B    | ~40GB | Slowest  | Best    | Research only |

**For our Elixir AI:**
- **Minimum:** mistral (7B)
- **Recommended:** codestral (22B)
- **Overkill:** llama3:70b

---

## 🧹 Cleaning Up Ollama

### Remove all unused layers:

```bash
# Ollama automatically cleans unused layers
# But you can force it:
ollama rm $(ollama list -q)
ollama pull codestral
```

### See what's actually using space:

```bash
# macOS/Linux
ls -lh ~/.ollama/models/manifests/registry.ollama.ai/library/
```

### Nuclear option (delete everything):

```bash
# WARNING: This deletes ALL models!
rm -rf ~/.ollama/models
```

Then re-pull what you need:
```bash
ollama pull codestral
```

---

## 🎛️ Advanced Management

### Change model storage location:

```bash
# Set environment variable
export OLLAMA_MODELS=/path/to/new/location

# Then start Ollama
ollama serve
```

### Run model with custom parameters:

```bash
ollama run codestral \
  --temperature 0.7 \
  --top-p 0.9 \
  --repeat-penalty 1.1
```

### Check what models are loaded in memory:

```bash
# While Ollama is running
curl http://localhost:11434/api/tags
```

---

## 💡 Best Practices

### 1. Keep Only What You Need

```bash
# Bad: Having 10 models (50+ GB)
ollama list | wc -l
# 10

# Good: 2-3 models you actually use
ollama rm unused-model-1
ollama rm unused-model-2
ollama rm unused-model-3
```

### 2. Use Tags Wisely

```bash
# Pull specific version
ollama pull codestral:latest

# Not needed - versions auto-update
ollama pull codestral:v1
ollama pull codestral:v2
```

### 3. Regular Cleanup

```bash
# Monthly: Check what you have
ollama list

# Remove unused
ollama rm old-experiments
```

### 4. Monitor Disk Space

```bash
# Check before pulling new models
df -h ~

# Check Ollama usage
du -sh ~/.ollama
```

---

## 🎯 Workflow for Our Elixir AI

### Initial Setup:

```bash
# Pull Codestral (our default)
ollama pull codestral

# Optional: Pull backup model
ollama pull deepseek-coder
```

### Weekly Maintenance:

```bash
# Check what you have
ollama list

# Update to latest
ollama pull codestral
```

### If Running Low on Disk:

```bash
# See what's taking space
du -sh ~/.ollama/models

# Remove unused models
ollama list
ollama rm unused-model
```

---

## 🐛 Troubleshooting

### "Model not found"

```bash
# List available models
ollama list

# Pull it
ollama pull codestral
```

### "Not enough disk space"

```bash
# Check space
df -h

# Remove old models
ollama rm old-model

# Or move to bigger drive
export OLLAMA_MODELS=/Volumes/BigDrive/ollama
ollama serve
```

### "Model corrupted"

```bash
# Remove and re-download
ollama rm codestral
ollama pull codestral
```

### "Ollama taking too much RAM"

```bash
# Models load into RAM when used
# Unload by stopping Ollama
pkill ollama

# Or restart
ollama serve
```

---

## 📊 Quick Commands Summary

```bash
# Essential Commands
ollama list                    # What do I have?
ollama pull <model>            # Download a model
ollama rm <model>              # Delete a model
ollama show <model>            # Model details
du -sh ~/.ollama/models        # Disk usage

# Maintenance
ollama pull codestral          # Update default model
ollama list | grep -v NAME     # List without header
df -h ~                        # Check disk space

# Testing
ollama run codestral           # Interactive chat
ollama run codestral "Hi!"     # One-off query
```

---

## 🎯 Recommended Setup for Elixir AI

### Minimal (8GB RAM, 20GB disk):

```bash
ollama pull codestral
# That's it! 4.1 GB
```

### Balanced (16GB RAM, 50GB disk):

```bash
ollama pull codestral      # Primary (4.1 GB)
ollama pull deepseek-coder # Backup (3.8 GB)
```

### Power User (32GB RAM, 100GB+ disk):

```bash
ollama pull codestral      # Code - 4.1 GB
ollama pull deepseek-coder # Fast code - 3.8 GB
ollama pull llama3         # General - 4.7 GB
```

---

## 🚀 Quick Start Checklist

- [ ] Install Ollama: `brew install ollama`
- [ ] Start server: `ollama serve`
- [ ] Pull model: `ollama pull codestral`
- [ ] Verify: `ollama list`
- [ ] Test: `ollama run codestral "Hello!"`
- [ ] Use in web UI: `./start_web_ui.sh`

---

## 📞 Getting Help

```bash
# Ollama help
ollama --help

# Command-specific help
ollama pull --help

# Version
ollama --version

# Server logs
# macOS/Linux: Check console/terminal where "ollama serve" runs
```

---

**You now know everything about managing Ollama models!** 🎉

**For our Elixir AI, just keep it simple:**
```bash
ollama pull codestral
```

**That's all you need!** 🚀
