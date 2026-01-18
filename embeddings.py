"""
embeddings.py

Embedding models for code semantic search.

For CODE specifically, we use:
- jinaai/jina-embeddings-v2-base-code - Optimized for code (768 dims)
- Fallback: sentence-transformers/all-MiniLM-L6-v2 (384 dims)

The code-specific model understands:
- Programming syntax and semantics
- Function signatures and documentation
- Code structure and patterns
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np


class HybridCodeEmbedder:
    """
    Code embedding model with metadata enhancement.
    
    This combines:
    1. Code-specific embeddings (semantic code understanding)
    2. Metadata enhancement (module names, function names)
    
    This gives better retrieval for both code and documentation.
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize embedding model
        
        Args:
            model_name: Specific model to use (optional)
                       Default tries Jina Code, falls back to MiniLM
        """
        print("Loading embedding models...")
        
        if model_name:
            self.code_encoder = SentenceTransformer(model_name)
            print(f"✓ Loaded {model_name}")
        else:
            # Try code-specific model first
            try:
                self.code_encoder = SentenceTransformer('jinaai/jina-embeddings-v2-base-code')
                print("✓ Loaded Jina Code Embeddings (768 dims)")
            except Exception as e:
                print(f"⚠ Jina model not available ({e}), using MiniLM")
                self.code_encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                print("✓ Loaded MiniLM Embeddings (384 dims)")
        
        self.embedding_dim = self.code_encoder.get_sentence_embedding_dimension()
        print(f"Embedding dimension: {self.embedding_dim}")
    
    def encode(self, text: str) -> np.ndarray:
        """
        Encode single text
        
        Args:
            text: Text to encode
            
        Returns:
            Embedding vector
        """
        return self.code_encoder.encode(text, convert_to_numpy=True)
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Encode multiple texts efficiently
        
        Args:
            texts: List of texts to encode
            batch_size: Batch size for encoding
            
        Returns:
            Array of embedding vectors
        """
        return self.code_encoder.encode(
            texts, 
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
    
    def encode_chunk(self, chunk: Dict) -> np.ndarray:
        """
        Encode a code chunk with metadata enhancement
        
        Strategy: Include metadata in embedding for better retrieval
        This helps match queries like "permission module" to the right code
        
        Args:
            chunk: Code chunk dictionary with metadata
            
        Returns:
            Embedding vector
        """
        text = chunk['text']
        
        # Enhance with metadata
        prefix = ""
        if 'module' in chunk:
            prefix += f"Module: {chunk['module']}\n"
        if 'functions' in chunk:
            prefix += f"Functions: {', '.join(chunk['functions'])}\n"
        if chunk.get('type') == 'module':
            prefix += "Type: Complete Module\n"
        
        enhanced_text = prefix + "\n" + text if prefix else text
        
        return self.encode(enhanced_text)


# Example usage
if __name__ == "__main__":
    # Test the embedder
    embedder = HybridCodeEmbedder()
    
    # Test single encoding
    test_code = """
    defmodule MyApp.User do
      def authenticate(username, password) do
        # Authentication logic
      end
    end
    """
    
    vector = embedder.encode(test_code)
    print(f"\nEncoded test code: vector shape = {vector.shape}")
    
    # Test batch encoding
    test_batch = [
        "def hello(name), do: \"Hello, #{name}\"",
        "defmodule Math do\n  def add(a, b), do: a + b\nend",
    ]
    
    vectors = embedder.encode_batch(test_batch)
    print(f"Encoded batch: vectors shape = {vectors.shape}")
