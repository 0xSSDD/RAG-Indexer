"""
test_installation.py

Quick test to verify your installation is working correctly.

Run this after setup to check everything is installed properly.
"""

import sys

def test_imports():
    """Test that all required packages are installed"""
    print("Testing imports...")
    
    required_packages = {
        'sentence_transformers': 'Sentence Transformers',
        'qdrant_client': 'Qdrant Client',
        'numpy': 'NumPy',
        'transformers': 'Transformers',
    }
    
    optional_packages = {
        'ollama': 'Ollama (for local LLM)',
        'anthropic': 'Anthropic (for Claude API)',
    }
    
    success = True
    
    # Test required packages
    print("\nRequired packages:")
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT FOUND")
            success = False
    
    # Test optional packages
    print("\nOptional packages:")
    for package, name in optional_packages.items():
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ⚠ {name} - not installed (okay if not using)")
    
    return success


def test_components():
    """Test that our custom modules work"""
    print("\n" + "="*50)
    print("Testing custom components...")
    
    try:
        from embeddings import HybridCodeEmbedder
        print("  ✓ embeddings.py")
        
        from vector_db import CodeVectorDB
        print("  ✓ vector_db.py")
        
        from code_chunker import ElixirCodeChunker
        print("  ✓ code_chunker.py")
        
        from rag_system import ElixirRAG
        print("  ✓ rag_system.py")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_embeddings():
    """Test embedding generation"""
    print("\n" + "="*50)
    print("Testing embedding generation...")
    
    try:
        from embeddings import HybridCodeEmbedder
        
        print("  Loading model (this may take a moment)...")
        embedder = HybridCodeEmbedder()
        
        print("  Testing single encoding...")
        test_text = "def hello, do: :world"
        vector = embedder.encode(test_text)
        
        print(f"  ✓ Generated embedding: shape={vector.shape}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    print("="*50)
    print("Elixir AI System - Installation Test")
    print("="*50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Some required packages are missing!")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Test components
    if not test_components():
        print("\n❌ Component test failed!")
        sys.exit(1)
    
    # Test embeddings
    if not test_embeddings():
        print("\n❌ Embedding test failed!")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("✅ All tests passed!")
    print("="*50)
    print("\nYour installation is working correctly!")
    print("\nNext steps:")
    print("  1. Edit index_hub88.py with your repo paths")
    print("  2. Run: python index_hub88.py")
    print("  3. Run: python query_hub88.py")


if __name__ == "__main__":
    main()
