"""
rag_system.py

Complete RAG (Retrieval Augmented Generation) system for Elixir code.

Features:
- Smart context retrieval
- Re-ranking for better results
- Support for both Ollama (Codestral) and Claude API
- Query optimization
"""

from embeddings import HybridCodeEmbedder
from vector_db import CodeVectorDB
from typing import List, Dict
import os

# Optional: Only imported if needed
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠ Ollama not installed. Install with: pip install ollama")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠ Anthropic not installed. Install with: pip install anthropic")


class ElixirRAG:
    """
    RAG system for Elixir code assistance

    Retrieves relevant code from your codebase and uses an LLM
    to generate informed responses.
    """

    def __init__(
        self,
        vector_db: CodeVectorDB,
        embedder: HybridCodeEmbedder,
        model: str = "codestral",
        use_claude: bool = False,
        claude_api_key: str = None
    ):
        """
        Initialize RAG system

        Args:
            vector_db: Initialized vector database
            embedder: Embedding model
            model: Model name for Ollama (if not using Claude)
            use_claude: Whether to use Claude API instead of Ollama
            claude_api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        """
        self.db = vector_db
        self.embedder = embedder
        self.model = model
        self.use_claude = use_claude

        if use_claude:
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic not installed. Run: pip install anthropic")

            api_key = claude_api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Claude API key required. Set ANTHROPIC_API_KEY or pass claude_api_key")

            self.claude_client = anthropic.Anthropic(api_key=api_key)
            print(f"✓ RAG System initialized (model=Claude)")
        else:
            if not OLLAMA_AVAILABLE:
                raise ImportError("Ollama not installed. Run: pip install ollama")
            print(f"✓ RAG System initialized (model={model})")

    def retrieve_context(
        self,
        query: str,
        k: int = 5,
        repo_filter: str = None,
        rerank: bool = True
    ) -> List:
        """
        Retrieve relevant code chunks

        Steps:
        1. Encode query
        2. Vector search
        3. (Optional) Re-rank results
        4. Return top-k

        Args:
            query: User query
            k: Number of results to return
            repo_filter: Filter by repository name
            rerank: Whether to re-rank results

        Returns:
            List of search results
        """
        # Encode query
        query_vector = self.embedder.encode(query)

        # Search (retrieve more than k for re-ranking)
        initial_k = k * 3 if rerank else k
        results = self.db.search(
            query_vector=query_vector,
            limit=initial_k,
            repo_filter=repo_filter,
            score_threshold=0.3  # Filter low-quality matches
        )

        if not results.points:
            print("⚠ No results found")
            return []

        # Re-rank if enabled
        if rerank and len(results.points) > k:
            reranked_points = self._rerank(query, results.points, k)
            return reranked_points[:k]

        return results.points[:k]

    def _rerank(self, query: str, results: List, k: int) -> List:
        """
        Re-rank results using heuristics

        Preferences:
        - Complete modules over chunks
        - Documented code
        - Multi-function chunks

        Args:
            query: Original query
            results: Search results
            k: Number of results to return

        Returns:
            Re-ranked results
        """
        def score(result):
            payload = result.payload
            score = result.score

            # Boost complete modules
            if payload.get('type') == 'module':
                score += 0.1

            # Boost documented code
            if payload.get('metadata', {}).get('has_docs'):
                score += 0.05

            # Boost multi-function chunks
            func_count = payload.get('metadata', {}).get('function_count', 0)
            score += min(func_count * 0.01, 0.05)

            return score

        # Re-sort by new score
        results = sorted(results, key=score, reverse=True)
        return results[:k]

    def build_prompt(self, query: str, context: List) -> str:
        """
        Build prompt with retrieved context

        Args:
            query: User question
            context: Retrieved code chunks

        Returns:
            Complete prompt for LLM
        """
        context_str = ""

        for i, result in enumerate(context, 1):
            payload = result.payload
            score = result.score

            context_str += f"\n{'='*80}\n"
            context_str += f"[Context {i}] (similarity: {score:.2f})\n"
            context_str += f"File: {payload['file']}\n"

            if payload.get('module'):
                context_str += f"Module: {payload['module']}\n"

            if payload.get('functions'):
                context_str += f"Functions: {', '.join(payload['functions'])}\n"

            context_str += f"\n{payload['text']}\n"

        prompt = f"""You are an expert Elixir developer working on the Hub88 gaming platform.

Here is relevant code from the codebase:
{context_str}

{'='*80}

Question: {query}

Instructions:
- Use the code examples above as reference
- Follow the patterns and conventions from the codebase
- Provide working, production-quality Elixir code
- Explain your approach briefly

Answer:"""

        return prompt

    def query(
        self,
        question: str,
        k: int = 5,
        repo_filter: str = None,
        verbose: bool = True
    ) -> str:
        """
        Main query interface - ask questions about your codebase

        Args:
            question: Question to ask
            k: Number of context chunks to retrieve
            repo_filter: Filter to specific repository
            verbose: Whether to print debug info

        Returns:
            Answer from LLM
        """
        if verbose:
            print(f"\n🔍 Query: {question}")
            print("="*80)

        # Retrieve context
        context = self.retrieve_context(
            query=question,
            k=k,
            repo_filter=repo_filter
        )

        if not context:
            return "No relevant code found in the codebase."

        if verbose:
            print(f"\n✓ Retrieved {len(context)} relevant chunks")
            for i, res in enumerate(context, 1):
                print(f"  {i}. {res.payload['file']} (score: {res.score:.2f})")

        # Build prompt
        prompt = self.build_prompt(question, context)

        # Query model
        if verbose:
            print(f"\n🤖 Querying {self.model if not self.use_claude else 'Claude'}...")

        if self.use_claude:
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.content[0].text
        else:
            # Use Ollama
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response['message']['content']

        return answer


# Example usage
if __name__ == "__main__":
    print("This module should be imported, not run directly.")
    print("See query_hub88.py for usage example.")
