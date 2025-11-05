# modules/memory.py → Memory Manager
# Role: Embedding-based semantic memory using FAISS.

# Responsibilities:

# Store & retrieve MemoryItem objects

# Use local embedding server (e.g., Ollama) to vectorize input

# Filter memory based on type/tags/session

# Dependencies:

# faiss, requests, pydantic

# Used by: context.py, loop.py

# Inputs: Queries and tool outputs

# Outputs: Retrieved memory items for context injection

# modules/memory.py

from typing import List, Optional, Literal
from pydantic import BaseModel
from datetime import datetime
import requests
import numpy as np
import faiss


class MemoryItem(BaseModel):
    text: str
    type: Literal["preference", "tool_output", "fact", "query", "system"] = "fact"
    timestamp: Optional[str] = datetime.now().isoformat()
    tool_name: Optional[str] = None
    user_query: Optional[str] = None
    tags: List[str] = []
    session_id: Optional[str] = None


class MemoryManager:
    def __init__(self, embedding_model_url: str, model_name: str = "nomic-embed-text"):
        self.embedding_model_url = embedding_model_url
        self.model_name = model_name
        self.index: Optional[faiss.IndexFlatL2] = None
        self.data: List[MemoryItem] = []
        self.embeddings: List[np.ndarray] = []
        self.embeddings_enabled = True  # Flag to track if embeddings are available
        
        # Test connection on initialization (non-blocking)
        self._test_embedding_connection()

    def _test_embedding_connection(self):
        """Test if the embedding service is available."""
        try:
            # Try a simple test request
            response = requests.post(
                self.embedding_model_url,
                json={"model": self.model_name, "prompt": "test"},
                timeout=2
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.embeddings_enabled = False
            print(f"[memory] ⚠️ Embedding service unavailable ({self.embedding_model_url}): {e}")
            print(f"[memory] Continuing without semantic memory. To enable embeddings:")
            print(f"[memory]   1. Ensure Ollama is running: `ollama serve`")
            print(f"[memory]   2. Pull the model: `ollama pull {self.model_name}`")

    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text, handling errors gracefully."""
        if not self.embeddings_enabled:
            raise RuntimeError("Embedding service is not available")
            
        try:
            response = requests.post(
                self.embedding_model_url,
                json={"model": self.model_name, "prompt": text},
                timeout=10
            )
            response.raise_for_status()
            return np.array(response.json()["embedding"], dtype=np.float32)
        except requests.exceptions.RequestException as e:
            # Disable embeddings on failure
            self.embeddings_enabled = False
            raise RuntimeError(f"Embedding service error: {e}")

    def add(self, item: MemoryItem):
        """Add item to memory. Falls back to simple storage if embeddings unavailable."""
        if self.embeddings_enabled:
            try:
                embedding = self._get_embedding(item.text)
                self.embeddings.append(embedding)
                
                # Init or add to index
                if self.index is None:
                    self.index = faiss.IndexFlatL2(len(embedding))
                self.index.add(np.stack([embedding]))
            except RuntimeError:
                # Embeddings failed, continue without semantic search
                self.embeddings_enabled = False
        
        # Always store the data item even if embeddings fail
        self.data.append(item)

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        type_filter: Optional[str] = None,
        tag_filter: Optional[List[str]] = None,
        session_filter: Optional[str] = None
    ) -> List[MemoryItem]:
        """Retrieve memory items. Falls back to simple filtering if embeddings unavailable."""
        if not self.data:
            return []

        # If embeddings are disabled, use simple text matching and filtering
        if not self.embeddings_enabled or not self.index:
            results = []
            for item in self.data:
                # Apply filters
                if type_filter and item.type != type_filter:
                    continue
                if tag_filter and not any(tag in item.tags for tag in tag_filter):
                    continue
                if session_filter and item.session_id != session_filter:
                    continue
                results.append(item)
            # Return most recent items matching filters
            return results[:top_k]

        # Use semantic search when embeddings are available
        try:
            query_vec = self._get_embedding(query).reshape(1, -1)
            D, I = self.index.search(query_vec, top_k * 2)  # overfetch for filtering

            results = []
            for idx in I[0]:
                if idx >= len(self.data):
                    continue
                item = self.data[idx]

                if type_filter and item.type != type_filter:
                    continue
                if tag_filter and not any(tag in item.tags for tag in tag_filter):
                    continue
                if session_filter and item.session_id != session_filter:
                    continue

                results.append(item)
                if len(results) >= top_k:
                    break

            return results
        except RuntimeError:
            # Embeddings failed during retrieval, fall back to simple filtering
            self.embeddings_enabled = False
            return self.retrieve(query, top_k, type_filter, tag_filter, session_filter)

    def bulk_add(self, items: List[MemoryItem]):
        for item in items:
            self.add(item)
