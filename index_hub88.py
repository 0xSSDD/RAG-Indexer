"""
index_hub88.py

Main script to index your Hub88 repositories into the vector database.

Usage:
    python index_hub88.py

Before running:
1. Edit the 'repos' list below with your actual repository paths
2. Make sure Ollama is running if you plan to use it (ollama serve)
3. Install dependencies: pip install -r requirements.txt
"""

from code_chunker import chunk_repository
from embeddings import HybridCodeEmbedder
from vector_db import CodeVectorDB
from pathlib import Path
from typing import List
import json
import sys


def index_repositories(repo_paths: List[str], collection_name: str = "elixir_code"):
    """
    Index multiple repositories into Qdrant

    Args:
        repo_paths: List of paths to repositories
        collection_name: Name for the Qdrant collection
    """
    print("="*80)
    print("INDEXING HUB88 REPOSITORIES")
    print("="*80)

    # Validate paths
    valid_repos = []
    for repo_path in repo_paths:
        if Path(repo_path).exists():
            valid_repos.append(repo_path)
            print(f"✓ Found: {repo_path}")
        else:
            print(f"⚠ Path not found: {repo_path}")

    if not valid_repos:
        print("\n❌ No valid repository paths found!")
        print("Please edit the 'repos' list in this file with your actual paths.")
        sys.exit(1)

    print(f"\n📁 Will index {len(valid_repos)} repositories")

    # Initialize components
    print("\n" + "="*80)
    print("INITIALIZING COMPONENTS")
    print("="*80)

    embedder = HybridCodeEmbedder()
    db = CodeVectorDB(collection_name=collection_name)

    # Create collection
    db.create_collection(embedding_dim=embedder.embedding_dim)

    # Process each repository
    print("\n" + "="*80)
    print("CHUNKING CODE")
    print("="*80)

    all_chunks = []

    for repo_path in valid_repos:
        print(f"\n📁 Processing: {repo_path}")
        chunks = chunk_repository(repo_path)
        all_chunks.extend(chunks)

    print(f"\n✓ Total chunks: {len(all_chunks)}")

    if not all_chunks:
        print("❌ No Elixir code found in repositories!")
        sys.exit(1)

    # Generate embeddings
    print("\n" + "="*80)
    print("GENERATING EMBEDDINGS")
    print("="*80)

    texts = [chunk['text'] for chunk in all_chunks]
    embeddings = embedder.encode_batch(texts, batch_size=32)

    # Index into Qdrant
    print("\n" + "="*80)
    print("UPLOADING TO QDRANT")
    print("="*80)

    db.index_chunks(all_chunks, embeddings)

    # Save metadata
    metadata = {
        'repos': repo_paths,
        'total_chunks': len(all_chunks),
        'embedding_dim': embedder.embedding_dim,
        'collection_name': collection_name
    }

    with open('index_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    print("\n" + "="*80)
    print("✅ INDEXING COMPLETE!")
    print("="*80)
    print(f"Indexed {len(all_chunks)} chunks from {len(valid_repos)} repositories")
    print(f"Collection: {collection_name}")
    print(f"Metadata saved to: index_metadata.json")
    print("\n💡 You can now query your codebase with: python query_hub88.py")

    return db, embedder


if __name__ == "__main__":
    # ========================================================================
    # CONFIGURE YOUR REPOSITORIES HERE
    # ========================================================================

    # OPTION 1: Edit this list with your actual Hub88 repository paths
    repos = [
        # Example paths - replace with your actual paths:
        # "/Users/arpan/hub88/backend",
        # "/Users/arpan/hub88/schemas",
        # "/home/arpan/projects/hub88/core",

        # For testing, you can use any Elixir repo:
        # "/path/to/any/elixir/project",
    ]

    # OPTION 2: Read from environment variable
    # Uncomment this to read from HUB88_REPOS env var (colon-separated paths)
    # import os
    # env_repos = os.getenv('HUB88_REPOS', '')
    # if env_repos:
    #     repos = env_repos.split(':')

    # ========================================================================

    if not repos:
        print("\n" + "="*80)
        print("⚠ NO REPOSITORIES CONFIGURED")
        print("="*80)
        print("\nPlease edit this file (index_hub88.py) and add your repository paths.")
        print("\nExample:")
        print('    repos = [')
        print('        "/path/to/hub88/backend",')
        print('        "/path/to/hub88/schemas",')
        print('    ]')
        print("\nOr set environment variable:")
        print('    export HUB88_REPOS="/path/to/repo1:/path/to/repo2"')
        sys.exit(1)

    # Run indexing
    index_repositories(repos)
