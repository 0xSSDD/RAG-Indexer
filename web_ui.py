"""
web_ui.py

Simple web interface for the Elixir RAG system using Streamlit.

Run with: streamlit run web_ui.py
"""

import streamlit as st
import os
from pathlib import Path
import json

# Only import RAG components when needed
@st.cache_resource
def load_rag_system(use_claude=False):
    """Load RAG system (cached to avoid reloading)"""
    from embeddings import HybridCodeEmbedder
    from vector_db import CodeVectorDB
    from rag_system import ElixirRAG
    
    embedder = HybridCodeEmbedder()
    db = CodeVectorDB(collection_name="hub88_code")
    
    # Check if index exists
    if not os.path.exists('./qdrant_data'):
        return None, "Please index your code first!"
    
    rag = ElixirRAG(
        vector_db=db,
        embedder=embedder,
        model=os.getenv('OLLAMA_MODEL', 'codestral'),
        use_claude=use_claude
    )
    
    return rag, None

# Page config
st.set_page_config(
    page_title="Elixir AI Assistant",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #6B46C1;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
    .code-block {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #d4d4d4;
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://elixir-lang.org/images/logo/logo.png", width=100)
    st.title("⚙️ Settings")
    
    # LLM Selection
    use_claude = st.checkbox("Use Claude API", value=False)
    
    if use_claude:
        api_key = st.text_input("Claude API Key", type="password", 
                                value=os.getenv('ANTHROPIC_API_KEY', ''))
        if api_key:
            os.environ['ANTHROPIC_API_KEY'] = api_key
    else:
        ollama_model = st.selectbox(
            "Ollama Model",
            ["codestral", "deepseek-coder", "llama3", "mistral"],
            index=0
        )
        os.environ['OLLAMA_MODEL'] = ollama_model
    
    st.divider()
    
    # Query Settings
    st.subheader("🔍 Query Settings")
    num_chunks = st.slider("Context Chunks", 1, 10, 5)
    repo_filter = st.text_input("Filter by Repo (optional)", "")
    
    st.divider()
    
    # Stats
    st.subheader("📊 System Stats")
    
    if os.path.exists('index_metadata.json'):
        with open('index_metadata.json', 'r') as f:
            metadata = json.load(f)
        
        st.metric("Indexed Chunks", metadata.get('total_chunks', 0))
        st.metric("Repositories", len(metadata.get('repos', [])))
        st.metric("Embedding Dim", metadata.get('embedding_dim', 0))
    else:
        st.warning("No index found. Run `python index_hub88.py` first!")
    
    st.divider()
    
    # Quick Actions
    st.subheader("🚀 Quick Actions")
    if st.button("📖 View README"):
        st.session_state.show_readme = True
    
    if st.button("🔄 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main Content
st.markdown('<p class="main-header">🧪 Elixir AI Assistant</p>', unsafe_allow_html=True)

# Show README if requested
if st.session_state.get('show_readme', False):
    with st.expander("📖 README", expanded=True):
        try:
            with open('README.md', 'r') as f:
                st.markdown(f.read())
        except:
            st.error("README.md not found")
    
    if st.button("Close README"):
        st.session_state.show_readme = False
        st.rerun()
    
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Example questions
if not st.session_state.messages:
    st.subheader("💡 Example Questions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔐 How do we handle permissions?"):
            st.session_state.example_query = "How do we handle permissions in Hub88?"
    
    with col2:
        if st.button("⚡ Show GenServer examples"):
            st.session_state.example_query = "Show me examples of GenServers in our codebase"
    
    with col3:
        if st.button("💾 Database query patterns"):
            st.session_state.example_query = "What's the pattern for database queries?"
    
    st.divider()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle example query
if "example_query" in st.session_state:
    prompt = st.session_state.example_query
    del st.session_state.example_query
else:
    # Chat input
    prompt = st.chat_input("Ask a question about your Elixir codebase...")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            # Load RAG system
            rag, error = load_rag_system(use_claude)
            
            if error:
                st.error(error)
                st.info("Run `python index_hub88.py` to index your code first!")
            else:
                try:
                    # Query
                    answer = rag.query(
                        prompt, 
                        k=num_chunks,
                        repo_filter=repo_filter if repo_filter else None,
                        verbose=False
                    )
                    
                    # Display answer
                    st.markdown(answer)
                    
                    # Add to history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer
                    })
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    
                    # Show helpful tips
                    with st.expander("💡 Troubleshooting"):
                        st.markdown("""
                        **Common Issues:**
                        
                        1. **Ollama not running:** Start with `ollama serve`
                        2. **Model not found:** Run `ollama pull codestral`
                        3. **No index:** Run `python index_hub88.py`
                        4. **Out of memory:** Reduce context chunks in sidebar
                        """)

# Footer
st.divider()
st.caption("Built with ❤️ for the Elixir community • Powered by RAG + Ollama/Claude")
