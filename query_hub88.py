"""
query_hub88.py

Interactive query interface for your indexed Hub88 codebase.

Usage:
    python query_hub88.py

Before running:
1. Make sure you've indexed your repos with: python index_hub88.py
2. Start Ollama if using it: ollama serve
3. Pull Codestral model: ollama pull codestral
   OR set ANTHROPIC_API_KEY for Claude

Interactive mode:
    Just run the script and type your questions!

Example questions:
    - How do we handle permissions in Hub88?
    - Show me an example of a GenServer
    - How is authentication implemented?
    - What's the pattern for database queries?
"""

from rag_system import ElixirRAG
from embeddings import HybridCodeEmbedder
from vector_db import CodeVectorDB
import sys
import os


def main():
    """
    Interactive query interface
    """
    # Check if index exists
    if not os.path.exists('./qdrant_data'):
        print("❌ No indexed data found!")
        print("\nPlease run indexing first:")
        print("    python index_hub88.py")
        sys.exit(1)
    
    # Configuration
    USE_CLAUDE = os.getenv('USE_CLAUDE', '').lower() == 'true'
    MODEL = os.getenv('OLLAMA_MODEL', 'codestral')  # or 'deepseek-coder', 'llama3', etc.
    
    print("="*80)
    print("HUB88 CODE ASSISTANT")
    print("="*80)
    
    # Load indexed database
    print("\nLoading indexed codebase...")
    embedder = HybridCodeEmbedder()
    db = CodeVectorDB(collection_name="hub88_code")
    
    # Show stats
    stats = db.get_stats()
    print(f"✓ Loaded collection: {stats['total_points']} code chunks")
    
    # Initialize RAG
    if USE_CLAUDE:
        if not os.getenv('ANTHROPIC_API_KEY'):
            print("\n⚠ ANTHROPIC_API_KEY not set!")
            print("Set it with: export ANTHROPIC_API_KEY='your-key'")
            print("Or use Ollama by default (set USE_CLAUDE=false)")
            sys.exit(1)
        
        print(f"✓ Using Claude API")
        rag = ElixirRAG(
            vector_db=db,
            embedder=embedder,
            use_claude=True
        )
    else:
        print(f"✓ Using Ollama with model: {MODEL}")
        print("  (Change model: export OLLAMA_MODEL='deepseek-coder')")
        rag = ElixirRAG(
            vector_db=db,
            embedder=embedder,
            model=MODEL,
            use_claude=False
        )
    
    # Interactive query loop
    print("\n" + "="*80)
    print("Ask questions about your codebase!")
    print("="*80)
    print("Commands:")
    print("  - Type your question and press Enter")
    print("  - 'quit' or 'exit' to quit")
    print("  - 'help' for example questions")
    print()
    
    while True:
        try:
            question = input("\n🤔 Question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if question.lower() == 'help':
                print_help()
                continue
            
            if not question:
                continue
            
            # Query the system
            answer = rag.query(question, k=5, verbose=True)
            
            print("\n" + "="*80)
            print("📝 Answer:")
            print("="*80)
            print(answer)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Try a different question or check your setup.")


def print_help():
    """Print example questions"""
    print("\n" + "="*80)
    print("EXAMPLE QUESTIONS")
    print("="*80)
    print("""
    General Patterns:
    - How do we handle errors in Hub88?
    - What's the pattern for database queries?
    - Show me how to create a new GenServer
    
    Specific Features:
    - How is user authentication implemented?
    - How do we handle permissions?
    - What's the structure of game provider integrations?
    
    Code Examples:
    - Show me an example of a Phoenix controller
    - How do we use Ecto schemas?
    - What's a typical supervisor tree in our app?
    
    Best Practices:
    - What naming conventions do we use?
    - How should I structure a new module?
    - What's our pattern for handling API requests?
    """)


if __name__ == "__main__":
    main()
