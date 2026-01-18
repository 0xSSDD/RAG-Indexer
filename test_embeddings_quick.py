#!/usr/bin/env python3
# python test_embeddings_quick.py /Users/arpan/Documents/hub88-snr-sol
"""
Quick test script to verify embeddings work
No indexing needed - just tests the core components
"""

print("🧪 Testing Elixir AI Components...")
print("=" * 50)

# Test 1: Import core modules
print("\n1️⃣ Testing imports...")
try:
    from embeddings import HybridCodeEmbedder
    from code_chunker import ElixirCodeChunker
    print("   ✓ Imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    print("\n   Make sure you're in the RAG directory and venv is activated:")
    print("   cd /Users/arpan/Documents/elixir-ai/RAG")
    print("   source venv/bin/activate")
    exit(1)

# Test 2: Initialize embedder
print("\n2️⃣ Testing embedder initialization...")
try:
    embedder = HybridCodeEmbedder()
    print(f"   ✓ Embedder loaded")
    print(f"   ✓ Embedding dimension: {embedder.embedding_dim}")
except Exception as e:
    print(f"   ❌ Embedder failed: {e}")
    exit(1)

# Test 3: Test embedding generation
print("\n3️⃣ Testing embedding generation...")
try:
    test_code = """
    defmodule TestModule do
      def hello(name) do
        "Hello, #{name}!"
      end
    end
    """

    vector = embedder.encode(test_code)
    print(f"   ✓ Generated embedding")
    print(f"   ✓ Vector shape: {vector.shape}")
    print(f"   ✓ Vector preview: [{vector[0]:.4f}, {vector[1]:.4f}, {vector[2]:.4f}, ...]")
except Exception as e:
    print(f"   ❌ Embedding failed: {e}")
    exit(1)

# Test 4: Test chunker
print("\n4️⃣ Testing code chunker...")
try:
    chunker = ElixirCodeChunker(max_chunk_size=500, overlap=100)

    test_elixir_code = """
defmodule MyApp.User do
  @moduledoc \"\"\"
  User module for authentication
  \"\"\"

  def authenticate(username, password) do
    # Authentication logic here
    {:ok, %{username: username}}
  end

  def create_user(attrs) do
    # Create user logic
    {:ok, %User{}}
  end
end

defmodule MyApp.Auth do
  def verify_token(token) do
    # Verify JWT token
    {:ok, %{user_id: 1}}
  end
end
    """

    # Save to temp file
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ex', delete=False) as f:
        f.write(test_elixir_code)
        temp_file = f.name

    chunks = chunker.chunk_file(temp_file, repo_name="test_repo")
    os.unlink(temp_file)

    print(f"   ✓ Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks, 1):
        module = chunk.get('module', 'N/A')
        chunk_type = chunk['type']
        print(f"   ✓ Chunk {i}: {chunk_type:20s} module={module}")

except Exception as e:
    print(f"   ❌ Chunking failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 5: Test batch embeddings
print("\n5️⃣ Testing batch embeddings...")
try:
    texts = [chunk['text'] for chunk in chunks]
    embeddings = embedder.encode_batch(texts, batch_size=4)
    print(f"   ✓ Generated {len(embeddings)} embeddings")
    print(f"   ✓ Embeddings shape: {embeddings.shape}")
except Exception as e:
    print(f"   ❌ Batch embedding failed: {e}")
    exit(1)

# Test 6: Test with real Elixir repo (if provided)
print("\n6️⃣ Testing with real Elixir code...")
import sys
if len(sys.argv) > 1:
    repo_path = sys.argv[1]
    print(f"   📁 Scanning: {repo_path}")

    from pathlib import Path
    elixir_files = list(Path(repo_path).rglob('*.ex'))[:5]  # Just first 5 files

    if elixir_files:
        print(f"   ✓ Found {len(elixir_files)} .ex files (showing first 5)")

        all_chunks = []
        for ex_file in elixir_files:
            try:
                chunks = chunker.chunk_file(str(ex_file), repo_name="test")
                all_chunks.extend(chunks)
                print(f"   ✓ {ex_file.name}: {len(chunks)} chunks")
            except Exception as e:
                print(f"   ⚠️  {ex_file.name}: {e}")

        print(f"\n   ✓ Total chunks from real code: {len(all_chunks)}")

        # Generate embeddings for real code
        if all_chunks:
            print(f"   🔄 Generating embeddings for {len(all_chunks)} chunks...")
            real_texts = [c['text'] for c in all_chunks]
            real_embeddings = embedder.encode_batch(real_texts, batch_size=8)
            print(f"   ✓ Generated {len(real_embeddings)} real embeddings!")
    else:
        print(f"   ⚠️  No .ex files found in {repo_path}")
else:
    print("   💡 Tip: Run with a path to test real code:")
    print("      python test_embeddings_quick.py /path/to/elixir/repo")

# Success!
print("\n" + "=" * 50)
print("✅ ALL TESTS PASSED!")
print("=" * 50)
print("\nYour embeddings are working perfectly! 🎉")
print("\n📊 Summary:")
print(f"   • Embedding model: working ✓")
print(f"   • Embedding dimension: {embedder.embedding_dim}")
print(f"   • Code chunker: working ✓")
print(f"   • Batch processing: working ✓")
print("\n🚀 Next steps:")
print("   1. Run: ./start_web_ui.sh")
print("   2. Add your Elixir repo paths")
print("   3. Click 'Start Indexing'")
print("   4. Start chatting!")
