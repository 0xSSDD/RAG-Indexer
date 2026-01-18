# Web UI Guide

## 🌐 Beautiful Web Interface for Your Elixir AI Assistant

Instead of using the CLI (`query_hub88.py`), you can now use a beautiful web interface!

---

## 🎨 Features

- ✅ **ChatGPT-like Interface** - Familiar chat experience
- ✅ **Real-time Responses** - Stream answers as they generate
- ✅ **Example Questions** - One-click quick starts
- ✅ **Model Selection** - Switch between Ollama models or Claude
- ✅ **Adjustable Settings** - Control context chunks, filters
- ✅ **System Stats** - See indexed code stats
- ✅ **Chat History** - Keeps conversation context
- ✅ **Dark Mode** - Easy on the eyes

---

## 🚀 Quick Start

### 1. Make sure you've indexed your code:

```bash
python index_hub88.py
```

### 2. Start the web UI:

```bash
# Make script executable
chmod +x start_web_ui.sh

# Launch
./start_web_ui.sh
```

**Or manually:**

```bash
source venv/bin/activate
streamlit run web_ui.py
```

### 3. Open your browser:

The app automatically opens at `http://localhost:8501`

---

## 🎯 Using the Interface

### Main Chat Area

Just type your question in the chat input at the bottom:

```
"How do we handle permissions?"
"Show me GenServer examples"
"What's the pattern for database queries?"
```

### Sidebar Settings

**🤖 LLM Selection:**
- Toggle "Use Claude API" for cloud-based responses
- Choose Ollama model (Codestral, DeepSeek, etc.)

**🔍 Query Settings:**
- **Context Chunks:** How many code examples to retrieve (1-10)
- **Filter by Repo:** Only search specific repository

**📊 System Stats:**
- See how many chunks indexed
- View repositories included
- Check embedding dimensions

### Example Questions

Click any example button to try:
- 🔐 "How do we handle permissions?"
- ⚡ "Show GenServer examples"
- 💾 "Database query patterns"

---

## ⚙️ Configuration

### Using Claude API

1. Check "Use Claude API" in sidebar
2. Enter your API key
3. Or set environment variable:
   ```bash
   export ANTHROPIC_API_KEY='your-key'
   ```

### Using Ollama (Default)

1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```

2. Pull your preferred model:
   ```bash
   ollama pull codestral
   # or
   ollama pull deepseek-coder
   ```

3. Select model in sidebar dropdown

---

## 🎨 Screenshots & Features

### Chat Interface
- Clean, modern design
- ChatGPT-like experience
- Code syntax highlighting
- Markdown support

### Settings Panel
- Model selection
- Context tuning
- Repository filtering
- Real-time stats

### Example Questions
- One-click quick starts
- Common use cases
- Pattern exploration

---

## 🐛 Troubleshooting

### "No index found"

**Solution:**
```bash
python index_hub88.py
```

### "Ollama connection refused"

**Solution:**
```bash
# In another terminal
ollama serve
```

### "Model not found"

**Solution:**
```bash
ollama pull codestral
```

### Port 8501 already in use

**Solution:**
```bash
# Stop other Streamlit apps or use different port
streamlit run web_ui.py --server.port 8502
```

### Chat not responding

**Checklist:**
1. ✓ Virtual environment activated?
2. ✓ Code indexed?
3. ✓ Ollama running (or Claude API key set)?
4. ✓ Model downloaded?

---

## 🔧 Advanced Usage

### Custom Port

```bash
streamlit run web_ui.py --server.port 8080
```

### Remote Access

```bash
streamlit run web_ui.py --server.address 0.0.0.0
```

**Warning:** Only do this on trusted networks!

### Custom Theme

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#6B46C1"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"
```

---

## 📝 Tips & Tricks

### Better Questions

✅ **Good:**
- "How do we implement authentication in Hub88?"
- "Show me examples of using Ecto in our codebase"
- "What's our pattern for error handling?"

❌ **Too Generic:**
- "What is Elixir?"
- "How does pattern matching work?"

### Using Filters

Filter by specific repository:
```
Repo filter: hub88_backend
Question: "How do we handle API requests?"
```

### Adjusting Context

- **More chunks (7-10):** Better for complex questions
- **Fewer chunks (3-5):** Faster responses, more focused

---

## 🎓 Comparison: CLI vs Web UI

| Feature | CLI (`query_hub88.py`) | Web UI (`web_ui.py`) |
|---------|------------------------|----------------------|
| Interface | Terminal | Browser |
| Chat History | No | Yes |
| Examples | Manual | One-click |
| Settings | Env vars | GUI |
| Stats | Manual check | Real-time |
| Multi-turn | Manual | Automatic |
| Best for | Scripts, automation | Interactive use |

---

## 🚀 What's Next?

### Deploy for Your Team

**Option 1: Shared Server**
```bash
# On server
streamlit run web_ui.py --server.address 0.0.0.0 --server.port 8501
```

Team accesses at: `http://your-server-ip:8501`

**Option 2: Docker**
```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "web_ui.py"]
```

### Add Authentication

Use `streamlit-authenticator`:
```bash
pip install streamlit-authenticator
```

### Custom Branding

- Replace logo in sidebar
- Update colors in CSS
- Add company name

---

## 💡 Pro Tips

1. **Bookmark it:** Add `localhost:8501` to browser favorites
2. **Keep Ollama running:** Run `ollama serve` in background
3. **Use example questions:** Great for team demos
4. **Share screenshots:** Show your team what's possible
5. **Iterate quickly:** Make changes, auto-reloads!

---

## 🆚 vs Other Tools

### vs Cursor ($20/mo)
- ✅ Free
- ✅ Local
- ✅ Open source
- ❌ No IDE integration

### vs Continue.dev
- ✅ Elixir-optimized
- ✅ Web interface
- ✅ Simpler setup
- ❌ No VS Code extension

### vs GitHub Copilot
- ✅ Free
- ✅ Works on entire codebase
- ✅ Customizable
- ❌ Not in-editor

---

## 📞 Support

**Issues?**
1. Check troubleshooting section above
2. Review README.md
3. Check terminal for errors

**Feature Requests?**
- The code is yours - modify `web_ui.py`!
- Add new sidebar options
- Change UI colors
- Add more example questions

---

**Enjoy your beautiful AI assistant! 🎉**
