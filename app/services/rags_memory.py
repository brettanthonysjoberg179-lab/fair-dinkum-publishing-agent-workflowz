#!/usr/bin/env python3
"""
RAGS memory module for Fair Dinkum Publishing.

Lightweight, zero-external-dependency implementation using:
- TF-IDF for embeddings (no sentence-transformers needed)
- SQLite for vector storage
- Automatic document chunking and retrieval

Integrates with the publishing agent pipeline so each agent can
store and retrieve context from past runs.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any, Optional
from collections import Counter

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# TF-IDF Embedding (zero external dependencies)
# ---------------------------------------------------------------------------

class TFIDFBackend:
    """Simple TF-IDF embedding backend. No external model downloads."""

    def __init__(self):
        self._vocabulary: dict[str, int] = {}
        self._idf: dict[str, float] = {}
        self._doc_count = 0

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization: lowercase, split on non-alphanumeric, filter short."""
        return [t for t in re.split(r'[^a-z0-9]+', text.lower()) if len(t) > 2]

    def _build_vocabulary(self, documents: list[str]):
        """Build vocabulary from a corpus of documents."""
        all_tokens: Counter = Counter()
        self._doc_count = len(documents)
        for doc in documents:
            tokens = set(self._tokenize(doc))
            all_tokens.update(tokens)

        # Filter to tokens that appear in at least 2 docs (if enough docs)
        self._vocabulary = {}
        idx = 0
        for token, count in all_tokens.most_common(10000):
            if self._doc_count > 1 and count < 2 and len(self._vocabulary) > 100:
                continue
            self._vocabulary[token] = idx
            idx += 1

        # Compute IDF
        self._idf = {}
        for token in self._vocabulary:
            doc_freq = sum(1 for doc in documents if token in doc.lower())
            self._idf[token] = math.log((self._doc_count + 1) / (doc_freq + 1)) + 1

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts as TF-IDF vectors."""
        if not self._vocabulary:
            self._build_vocabulary(texts)

        vectors = []
        dim = len(self._vocabulary)
        for text in texts:
            tokens = self._tokenize(text)
            vec = [0.0] * dim
            token_counts = Counter(tokens)
            total = len(tokens) or 1
            for token, count in token_counts.items():
                if token in self._vocabulary:
                    tf = count / total
                    idf = self._idf.get(token, 1.0)
                    vec[self._vocabulary[token]] = tf * idf
            # L2 normalize
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            vec = [v / norm for v in vec]
            vectors.append(vec)
        return vectors


# ---------------------------------------------------------------------------
# Vector Store
# ---------------------------------------------------------------------------

class VectorStore:
    """SQLite-backed vector storage with cosine similarity search."""

    def __init__(self, db_path: str = "./data/rags_vectors.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    source_type TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    metadata TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_source 
                ON chunks(source_type, source_id)
            """)
            conn.commit()

    def add(self, chunk_id: str, source_type: str, source_id: str,
            content: str, embedding: list[float], metadata: dict = None):
        """Add a chunk with its embedding."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO chunks 
                   (id, source_type, source_id, content, embedding, metadata, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (chunk_id, source_type, source_id, content,
                 json.dumps(embedding),
                 json.dumps(metadata or {}),
                 datetime.now(timezone.utc).isoformat())
            )
            conn.commit()

    def search(self, query_embedding: list[float], top_k: int = 5,
               source_type: str = None) -> list[dict]:
        """Search for top-k similar chunks using cosine similarity."""
        with sqlite3.connect(self.db_path) as conn:
            if source_type:
                rows = conn.execute(
                    "SELECT id, content, embedding, metadata, source_type, source_id FROM chunks WHERE source_type = ?",
                    (source_type,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, content, embedding, metadata, source_type, source_id FROM chunks"
                ).fetchall()

        results = []
        for row in rows:
            vec = json.loads(row[2])
            score = self._cosine_similarity(query_embedding, vec)
            results.append({
                "id": row[0],
                "content": row[1],
                "score": score,
                "metadata": json.loads(row[3]),
                "source_type": row[4],
                "source_id": row[5],
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
        norm_b = math.sqrt(sum(x * x for x in b)) or 1.0
        return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# Document Chunker
# ---------------------------------------------------------------------------

class DocumentChunker:
    """Split documents into overlapping chunks."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        """Split text into chunks with overlap."""
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            # Try to break on paragraph
            if end < len(text):
                para_break = text.rfind('\n\n', start, end)
                if para_break > start + self.chunk_size // 2:
                    end = para_break
            chunks.append(text[start:end].strip())
            start = end - self.overlap
        return chunks


# ---------------------------------------------------------------------------
# RAGS Memory (main interface)
# ---------------------------------------------------------------------------

class RAGSMemory:
    """RAG memory system for Fair Dinkum Publishing agents."""

    def __init__(self, db_path: str = "./data/rags_vectors.db",
                 chunk_size: int = 1000, overlap: int = 100, top_k: int = 5):
        self.store = VectorStore(db_path)
        self.chunker = DocumentChunker(chunk_size, overlap)
        self.backend = TFIDFBackend()
        self.top_k = top_k

    def remember(self, source_type: str, source_id: str, content: str,
                 metadata: dict = None) -> list[str]:
        """Store content in memory. Returns chunk IDs."""
        chunks = self.chunker.chunk(content)
        embeddings = self.backend.embed(chunks)
        chunk_ids = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = hashlib.md5(
                f"{source_type}:{source_id}:{i}:{chunk[:50]}".encode()
            ).hexdigest()
            self.store.add(
                chunk_id=chunk_id,
                source_type=source_type,
                source_id=source_id,
                content=chunk,
                embedding=embedding,
                metadata=metadata,
            )
            chunk_ids.append(chunk_id)

        return chunk_ids

    def recall(self, query: str, top_k: int = None,
               source_type: str = None) -> list[dict]:
        """Retrieve relevant memories for a query."""
        if not self.backend._vocabulary:
            # No data yet
            return []

        query_embedding = self.backend.embed([query])[0]
        return self.store.search(query_embedding, top_k or self.top_k, source_type)

    def recall_for_agent(self, agent_name: str, task_description: str,
                         project_id: str = None) -> str:
        """Retrieve context for an agent, formatted as a prompt section."""
        results = self.recall(task_description, top_k=self.top_k)

        if project_id:
            # Boost project-specific results
            project_results = [r for r in results if r.get("metadata", {}).get("project_id") == project_id]
            if project_results:
                results = project_results + [r for r in results if r not in project_results]

        if not results:
            return ""

        lines = ["## Relevant Past Work:"]
        for r in results:
            lines.append(f"\n[Score: {r['score']:.2f}] {r['content'][:300]}...")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Convenience functions for agent integration
# ---------------------------------------------------------------------------

_rags_instance: Optional[RAGSMemory] = None


def get_rags(db_path: str = "./data/rags_vectors.db") -> RAGSMemory:
    """Get or create the singleton RAGS instance."""
    global _rags_instance
    if _rags_instance is None:
        _rags_instance = RAGSMemory(db_path=db_path)
    return _rags_instance


def remember_research(project_id: str, research_data: dict) -> list[str]:
    """Store research findings in RAGS."""
    rags = get_rags()
    content = json.dumps(research_data, indent=2)
    return rags.remember("research", project_id, content,
                         metadata={"project_id": project_id, "type": "research"})


def remember_manuscript(project_id: str, manuscript_text: str) -> list[str]:
    """Store manuscript content in RAGS."""
    rags = get_rags()
    return rags.remember("manuscript", project_id, manuscript_text,
                         metadata={"project_id": project_id, "type": "manuscript"})


def remember_evaluation(project_id: str, evaluation_data: dict) -> list[str]:
    """Store evaluation results in RAGS."""
    rags = get_rags()
    content = json.dumps(evaluation_data, indent=2)
    return rags.remember("evaluation", project_id, content,
                         metadata={"project_id": project_id, "type": "evaluation"})


def recall_for_writing(project_id: str, task: str) -> str:
    """Get context for writing tasks."""
    rags = get_rags()
    return rags.recall_for_agent("manuscript_author", task, project_id)


def recall_for_evaluation(project_id: str, task: str) -> str:
    """Get context for evaluation tasks."""
    rags = get_rags()
    return rags.recall_for_agent("fact_check_compliance", task, project_id)


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    rags = get_rags()

    # Store something
    test_content = """
    The History of Graffiti: Walls That Talk is an ebook targeting street-art history 
    for skaters, writers, and culture fans. The research phase identified high demand 
    for authentic perspectives on graffiti culture. The manuscript uses a 10-chapter 
    structure covering origins in 1960s Philadelphia, the subway art movement, 
    legal vs illegal art, and modern street art culture.
    """
    ids = rags.remember("research", "FDP-TEST001", test_content,
                        metadata={"project_id": "FDP-TEST001", "title": "Graffiti History"})
    print(f"Stored {len(ids)} chunks")

    # Retrieve
    results = rags.recall("street art culture origins")
    print(f"Retrieved {len(results)} results:")
    for r in results:
        print(f"  [{r['score']:.2f}] {r['content'][:100]}...")
