"""
web_ui.py

Complete self-contained web interface for Elixir RAG system.
Handles setup, indexing, and querying - all in one place.

Run with: streamlit run web_ui.py
"""

import streamlit as st
import os
import sys
from pathlib import Path
import json
import subprocess
import time
from datetime import datetime
import requests

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="Elixir AI Assistant",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern, clean CSS
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Modern color palette */
    :root {
        --primary: #6B46C1;
        --secondary: #805AD5;
        --success: #48BB78;
        --warning: #ECC94B;
        --danger: #F56565;
        --bg-dark: #1A202C;
        --bg-light: #2D3748;
    }
    
    /* Clean header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Status cards */
    .status-card {
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid;
        margin: 1rem 0;
        background: rgba(255,255,255,0.05);
    }
    
    .status-success { border-color: var(--success); }
    .status-warning { border-color: var(--warning); }
    .status-error { border-color: var(--danger); }
    
    /* Buttons */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .assistant-message {
        background: rgba(255,255,255,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Helper Functions
# ============================================================================

def check_ollama_running():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434", timeout=1)
        return True
    except:
        return False

def check_ollama_model(model_name):
    """Check if a specific model is available"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return model_name in result.stdout
    except:
        return False

def get_index_status():
    """Get indexing status"""
    if not os.path.exists('qdrant_data'):
        return "not_indexed", {}
    
    if os.path.exists('index_metadata.json'):
        try:
            with open('index_metadata.json', 'r') as f:
                metadata = json.load(f)
            return "indexed", metadata
        except:
            return "error", {}
    
    return "unknown", {}

def run_indexing(repo_paths, progress_callback=None):
    """Run indexing in background"""
    from code_chunker import chunk_repository
    from embeddings import HybridCodeEmbedder
    from vector_db import CodeVectorDB
    
    try:
        # Initialize
        if progress_callback:
            progress_callback("Initializing embeddings model...")
        
        embedder = HybridCodeEmbedder()
        db = CodeVectorDB(collection_name="hub88_code")
        db.create_collection(embedding_dim=embedder.embedding_dim)
        
        # Process repos
        all_chunks = []
        for i, repo_path in enumerate(repo_paths):
            if progress_callback:
                progress_callback(f"Chunking repository {i+1}/{len(repo_paths)}: {repo_path}")
            
            chunks = chunk_repository(repo_path)
            all_chunks.extend(chunks)
        
        # Generate embeddings
        if progress_callback:
            progress_callback(f"Generating embeddings for {len(all_chunks)} chunks...")
        
        texts = [chunk['text'] for chunk in all_chunks]
        embeddings = embedder.encode_batch(texts, batch_size=32)
        
        # Index
        if progress_callback:
            progress_callback("Uploading to vector database...")
        
        db.index_chunks(all_chunks, embeddings)
        
        # Save metadata
        metadata = {
            'repos': repo_paths,
            'total_chunks': len(all_chunks),
            'embedding_dim': embedder.embedding_dim,
            'collection_name': 'hub88_code',
            'indexed_at': datetime.now().isoformat()
        }
        
        with open('index_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return True, metadata
    
    except Exception as e:
        return False, str(e)

@st.cache_resource
def load_rag_system(use_claude=False, claude_api_key=None):
    """Load RAG system (cached)"""
    try:
        from embeddings import HybridCodeEmbedder
        from vector_db import CodeVectorDB
        from rag_system import ElixirRAG
        
        embedder = HybridCodeEmbedder()
        db = CodeVectorDB(collection_name="hub88_code")
        
        rag = ElixirRAG(
            vector_db=db,
            embedder=embedder,
            model=os.getenv('OLLAMA_MODEL', 'codestral'),
            use_claude=use_claude,
            claude_api_key=claude_api_key
        )
        
        return rag, None
    except Exception as e:
        return None, str(e)

# ============================================================================
# Sidebar - System Status & Settings
# ============================================================================

with st.sidebar:
    st.markdown("### 🧪 Elixir AI")
    st.markdown("---")
    
    # System Status
    st.markdown("### 📊 System Status")
    
    # Check Ollama
    ollama_running = check_ollama_running()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Ollama Server**")
    with col2:
        if ollama_running:
            st.markdown("🟢")
        else:
            st.markdown("🔴")
    
    if not ollama_running:
        st.info("Start Ollama: `ollama serve`")
    
    # Check Index
    index_status, index_metadata = get_index_status()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Code Index**")
    with col2:
        if index_status == "indexed":
            st.markdown("🟢")
        else:
            st.markdown("🔴")
    
    if index_status == "indexed":
        st.metric("Chunks", index_metadata.get('total_chunks', 0))
        st.metric("Repos", len(index_metadata.get('repos', [])))
    
    st.markdown("---")
    
    # LLM Selection
    st.markdown("### 🤖 AI Model")
    
    llm_choice = st.radio(
        "Choose AI",
        ["Ollama (Local)", "Claude (API)"],
        help="Ollama runs locally, Claude uses API"
    )
    
    use_claude = llm_choice == "Claude (API)"
    
    if use_claude:
        claude_key = st.text_input(
            "API Key",
            type="password",
            value=os.getenv('ANTHROPIC_API_KEY', ''),
            help="Get from console.anthropic.com"
        )
    else:
        ollama_model = st.selectbox(
            "Model",
            ["codestral", "deepseek-coder", "llama3", "mistral"],
            help="Install: ollama pull [model]"
        )
        os.environ['OLLAMA_MODEL'] = ollama_model
        
        # Check if model exists
        if ollama_running and not check_ollama_model(ollama_model):
            st.warning(f"Run: `ollama pull {ollama_model}`")
    
    st.markdown("---")
    
    # Query Settings
    st.markdown("### ⚙️ Settings")
    
    num_chunks = st.slider(
        "Context Chunks",
        min_value=1,
        max_value=10,
        value=5,
        help="More chunks = more context, slower"
    )
    
    repo_filter = st.text_input(
        "Filter Repo",
        placeholder="hub88_backend",
        help="Optional: search specific repo"
    )
    
    st.markdown("---")
    
    # Actions
    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("📖 Help", use_container_width=True):
        st.session_state.show_help = True

# ============================================================================
# Main Content
# ============================================================================

st.markdown('<p class="main-header">🧪 Elixir AI Assistant</p>', unsafe_allow_html=True)

# Help/Setup Screen
if st.session_state.get('show_help', False) or index_status == "not_indexed":
    
    tab1, tab2, tab3 = st.tabs(["🚀 Quick Start", "📁 Index Code", "❓ Help"])
    
    with tab1:
        st.markdown("## Quick Start Guide")
        
        st.markdown("### 1️⃣ Start Ollama")
        st.code("ollama serve", language="bash")
        
        st.markdown("### 2️⃣ Pull a Model")
        st.code("ollama pull codestral", language="bash")
        
        st.markdown("### 3️⃣ Index Your Code")
        st.markdown("Use the **Index Code** tab →")
        
        st.markdown("### 4️⃣ Start Chatting!")
        st.markdown("Ask questions about your Elixir codebase")
        
        if st.button("Got it! 👍"):
            st.session_state.show_help = False
            st.rerun()
    
    with tab2:
        st.markdown("## 📁 Index Your Code")
        
        st.info("Add paths to your Elixir repositories. This only needs to be done once!")
        
        # Initialize repo paths in session state
        if 'repo_paths' not in st.session_state:
            st.session_state.repo_paths = ['']
        
        # Add/remove repo paths
        st.markdown("### Repository Paths")
        
        for i, path in enumerate(st.session_state.repo_paths):
            col1, col2 = st.columns([5, 1])
            
            with col1:
                new_path = st.text_input(
                    f"Repo {i+1}",
                    value=path,
                    key=f"repo_path_{i}",
                    placeholder="/Users/you/your-project"
                )
                st.session_state.repo_paths[i] = new_path
            
            with col2:
                if len(st.session_state.repo_paths) > 1:
                    if st.button("❌", key=f"remove_{i}"):
                        st.session_state.repo_paths.pop(i)
                        st.rerun()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ Add Repository", use_container_width=True):
                st.session_state.repo_paths.append('')
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.repo_paths = ['']
                st.rerun()
        
        st.markdown("---")
        
        # Index button
        valid_paths = [p for p in st.session_state.repo_paths if p and Path(p).exists()]
        
        if valid_paths:
            st.success(f"✓ {len(valid_paths)} valid repository path(s)")
            
            if st.button("🚀 Start Indexing", type="primary", use_container_width=True):
                st.session_state.indexing = True
                st.rerun()
        else:
            st.error("❌ No valid repository paths")
        
        # Show indexing progress
        if st.session_state.get('indexing', False):
            st.markdown("### 🔄 Indexing in Progress...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(message):
                status_text.markdown(f"**{message}**")
            
            # Run indexing
            success, result = run_indexing(valid_paths, update_progress)
            
            progress_bar.progress(100)
            
            if success:
                st.success("✅ Indexing Complete!")
                st.json(result)
                st.balloons()
                time.sleep(2)
                st.session_state.indexing = False
                st.session_state.show_help = False
                st.rerun()
            else:
                st.error(f"❌ Indexing Failed: {result}")
                st.session_state.indexing = False
    
    with tab3:
        st.markdown("## ❓ Help & Troubleshooting")
        
        st.markdown("### Common Issues")
        
        with st.expander("🔴 Ollama Server Not Running"):
            st.markdown("""
            **Solution:**
            ```bash
            ollama serve
            ```
            Keep this running in a separate terminal.
            """)
        
        with st.expander("⚠️ Model Not Found"):
            st.markdown("""
            **Solution:**
            ```bash
            ollama pull codestral
            # or
            ollama pull deepseek-coder
            ```
            """)
        
        with st.expander("❌ No Index Found"):
            st.markdown("""
            **Solution:**
            Go to the **Index Code** tab and add your repository paths.
            """)
        
        with st.expander("🐌 Slow Responses"):
            st.markdown("""
            **Solutions:**
            - Reduce context chunks in sidebar (try 3 instead of 5)
            - Use a smaller model (llama3 instead of codestral)
            - Ensure Ollama is running locally, not remote
            """)
        
        st.markdown("### Documentation")
        
        st.markdown("- 📖 [README.md](README.md)")
        st.markdown("- 🚀 [QUICKSTART.md](docs/QUICKSTART.md)")
        st.markdown("- 🌐 [WEB_UI_GUIDE.md](docs/WEB_UI_GUIDE.md)")

# ============================================================================
# Chat Interface (only show if indexed)
# ============================================================================

elif index_status == "indexed":
    
    # Check if ready to chat
    ready_to_chat = True
    warnings = []
    
    if use_claude:
        if not claude_key:
            ready_to_chat = False
            warnings.append("⚠️ Claude API key required")
    else:
        if not ollama_running:
            ready_to_chat = False
            warnings.append("⚠️ Ollama not running")
        elif not check_ollama_model(ollama_model):
            ready_to_chat = False
            warnings.append(f"⚠️ Model '{ollama_model}' not installed")
    
    # Show warnings
    if warnings:
        for warning in warnings:
            st.warning(warning)
        st.info("Fix the issues above to start chatting")
        st.stop()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Example questions (only show if no messages)
    if not st.session_state.messages:
        st.markdown("### 💡 Try asking:")
        
        col1, col2, col3 = st.columns(3)
        
        examples = [
            ("🔐 Permissions", "How do we handle permissions in our codebase?"),
            ("⚡ GenServers", "Show me examples of GenServers"),
            ("💾 Database", "What's our pattern for database queries?"),
        ]
        
        for col, (label, question) in zip([col1, col2, col3], examples):
            with col:
                if st.button(label, use_container_width=True):
                    st.session_state.example_question = question
    
    st.markdown("---")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle example question
    if "example_question" in st.session_state:
        prompt = st.session_state.example_question
        del st.session_state.example_question
    else:
        # Chat input
        prompt = st.chat_input("Ask about your Elixir code...")
    
    # Process message
    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Load RAG
                    rag, error = load_rag_system(
                        use_claude=use_claude,
                        claude_api_key=claude_key if use_claude else None
                    )
                    
                    if error:
                        st.error(f"Error loading RAG: {error}")
                    else:
                        # Query
                        answer = rag.query(
                            prompt,
                            k=num_chunks,
                            repo_filter=repo_filter if repo_filter else None,
                            verbose=False
                        )
                        
                        st.markdown(answer)
                        
                        # Save to history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer
                        })
                
                except Exception as e:
                    error_msg = f"**Error:** {str(e)}"
                    st.error(error_msg)
                    
                    # Save error to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

else:
    st.error("Unknown index status. Try re-indexing your code.")
