"""
hr_agent/vector_store.py
Persistent ChromaDB Vector Store Manager for local semantic search.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from .config import config

class HRVectorStore:
    """Manages persistent ChromaDB vector store for HR policy documents."""

    def __init__(self, persist_dir: Optional[Path] = None, collection_name: Optional[str] = None):
        self.persist_dir = Path(persist_dir or config.chroma_db_dir)
        self.collection_name = collection_name or config.collection_name
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Company HR Policy Documents Semantic Index"}
        )

    def add_chunks(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        if not documents:
            return
        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        where_clause = {"category": category} if category else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_clause
        )

        matched_items = []
        if not results or not results["documents"] or not results["documents"][0]:
            return matched_items

        docs = results["documents"][0]
        metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
        distances = results["distances"][0] if results["distances"] else [0.0] * len(docs)
        ids = results["ids"][0] if results["ids"] else [""] * len(docs)

        for doc_text, meta, dist, chunk_id in zip(docs, metas, distances, ids):
            similarity = round(max(0.0, 1.0 - (dist / 2.0)), 4) if dist is not None else 1.0
            matched_items.append({
                "chunk_id": chunk_id,
                "content": doc_text,
                "metadata": meta,
                "similarity_score": similarity,
                "source": meta.get("source_file", "Unknown"),
                "policy_title": meta.get("policy_title", "HR Policy"),
                "section": meta.get("section_title", "General")
            })

        return matched_items

    def count(self) -> int:
        return self.collection.count()
