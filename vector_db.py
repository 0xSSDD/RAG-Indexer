"""
vector_db.py

Qdrant vector database setup with optimizations for code search.

Features:
- Cosine distance for semantic similarity
- Payload indexing for fast filtering
- Batch upload support
- Hybrid search capabilities
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue,
    SearchParams
)
from typing import List, Dict
import uuid
import numpy as np


class CodeVectorDB:
    """
    Vector database for code search using Qdrant
    
    Supports:
    - Semantic similarity search
    - Filtering by repository, module, type
    - Score thresholds for quality
    """
    
    def __init__(self, path: str = "./qdrant_data", collection_name: str = "elixir_code"):
        """
        Initialize Qdrant vector database
        
        Args:
            path: Local storage path (use URL like "http://localhost:6333" for hosted)
            collection_name: Name of the collection
        """
        self.client = QdrantClient(path=path)
        self.collection_name = collection_name
        
        print(f"Initialized Qdrant at {path}")
    
    def create_collection(self, embedding_dim: int = 768, reset: bool = True):
        """
        Create collection with optimal settings for code search
        
        Distance metric: COSINE is best for semantic similarity
        
        Args:
            embedding_dim: Dimension of embeddings
            reset: Whether to delete existing collection
        """
        if reset:
            try:
                self.client.delete_collection(self.collection_name)
                print(f"Deleted existing collection: {self.collection_name}")
            except:
                pass
        
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=embedding_dim,
                distance=Distance.COSINE,  # Best for code similarity
            ),
        )
        
        # Create payload indexes for fast filtering
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="repo",
            field_schema="keyword"
        )
        
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="module",
            field_schema="keyword"
        )
        
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="type",
            field_schema="keyword"
        )
        
        print(f"✓ Created collection: {self.collection_name} (dim={embedding_dim})")
    
    def index_chunks(self, chunks: List[Dict], embeddings: np.ndarray, batch_size: int = 100):
        """
        Index chunks with embeddings into Qdrant
        
        Args:
            chunks: List of code chunks
            embeddings: Corresponding embeddings
            batch_size: Batch size for upload
        """
        points = []
        
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = PointStruct(
                id=str(uuid.uuid4()),  # Use UUID for unique IDs
                vector=embedding.tolist(),
                payload={
                    'text': chunk['text'],
                    'file': str(chunk['file']),
                    'repo': chunk['repo'],
                    'type': chunk['type'],
                    'module': chunk.get('module', ''),
                    'functions': chunk.get('functions', []),
                    'metadata': chunk.get('metadata', {}),
                }
            )
            points.append(point)
        
        # Upload in batches
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
            print(f"Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
        
        print(f"✓ Indexed {len(chunks)} chunks")
    
    def search(
        self, 
        query_vector: np.ndarray, 
        limit: int = 5,
        repo_filter: str = None,
        module_filter: str = None,
        score_threshold: float = 0.5
    ) -> List:
        """
        Search with optional filtering
        
        Args:
            query_vector: Query embedding
            limit: Number of results
            repo_filter: Filter by repository name
            module_filter: Filter by module name
            score_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of search results with scores and payloads
        """
        # Build filter
        filter_conditions = []
        
        if repo_filter:
            filter_conditions.append(
                FieldCondition(key="repo", match=MatchValue(value=repo_filter))
            )
        
        if module_filter:
            filter_conditions.append(
                FieldCondition(key="module", match=MatchValue(value=module_filter))
            )
        
        search_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=limit,
            query_filter=search_filter,
            score_threshold=score_threshold,
            search_params=SearchParams(
                hnsw_ef=128,  # Higher = better quality, slower
                exact=False   # Set True for exact search (slower)
            )
        )
        
        return results
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        info = self.client.get_collection(self.collection_name)
        return {
            'total_points': info.points_count,
            'vector_dim': info.config.params.vectors.size,
            'distance': info.config.params.vectors.distance
        }


# Example usage
if __name__ == "__main__":
    # Test the database
    db = CodeVectorDB(collection_name="test_collection")
    db.create_collection(embedding_dim=384)
    
    # Test data
    test_chunks = [
        {
            'text': 'def hello, do: "world"',
            'file': 'test.ex',
            'repo': 'test_repo',
            'type': 'module'
        }
    ]
    
    # Mock embeddings
    test_embeddings = np.random.randn(1, 384)
    
    # Index
    db.index_chunks(test_chunks, test_embeddings)
    
    # Stats
    stats = db.get_stats()
    print(f"\nCollection stats: {stats}")
    
    # Search
    query_vector = np.random.randn(384)
    results = db.search(query_vector, limit=1)
    print(f"Search results: {len(results)} found")
