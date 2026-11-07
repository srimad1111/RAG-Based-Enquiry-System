"""
Phase 4: BM25 Sparse Keyword Retriever Module.
Provides lexical retrieval over SQLite document chunks strictly partitioned by product version.
"""
import re
import sqlite3
from typing import Any, Dict, List, Optional
from rank_bm25 import BM25Okapi

from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()

# Standard stop words to ignore during lexical tokenization
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does",
    "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had",
    "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd",
    "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself",
    "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off",
    "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd",
    "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}


def tokenize_text(text: str) -> List[str]:
    """Tokenize text into lowercase alpha-numeric terms, filtering out stopwords."""
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z0-9_\-\.]+\b", text.lower())
    return [w for w in words if len(w) > 1 and w not in STOP_WORDS]


class BM25Retriever:
    """
    In-memory BM25 index partitioned by product version over SQLite document chunks.
    Ensures that lexical searches for a target version never inspect or return chunks
    from other product versions.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(settings.sqlite_path if db_path is None else db_path)
        # Partitioned index cache: { product_version: {"bm25": BM25Okapi, "chunks": List[Dict]} }
        self._version_indices: Dict[str, Dict[str, Any]] = {}

    def invalidate_cache(self, product_version: Optional[str] = None) -> None:
        """Clear cache for a specific version or all versions upon document updates."""
        if product_version:
            self._version_indices.pop(product_version, None)
            logger.info(f"BM25 index cache cleared for version: {product_version}")
        else:
            self._version_indices.clear()
            logger.info("BM25 index cache cleared for all versions.")

    def _build_version_index(self, product_version: str) -> Optional[Dict[str, Any]]:
        """Query SQLite and build an in-memory BM25 index for the target version."""
        query_sql = """
            SELECT 
                c.id AS chunk_id,
                c.document_id,
                d.document_name,
                d.product_name,
                d.product_version,
                d.document_type,
                c.section_title,
                c.page_number,
                c.text_content
            FROM document_chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE d.product_version = ?
            ORDER BY d.document_name, c.chunk_index ASC
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(query_sql, (product_version,)).fetchall()

            if not rows:
                logger.warning(f"No chunks found in SQLite for version '{product_version}'.")
                return None

            chunks: List[Dict[str, Any]] = []
            corpus_tokens: List[List[str]] = []

            for r in rows:
                chunk_dict = {
                    "chunk_id": r["chunk_id"],
                    "document_id": r["document_id"],
                    "document_name": r["document_name"],
                    "product_name": r["product_name"],
                    "product_version": r["product_version"],
                    "document_type": r["document_type"],
                    "section_title": r["section_title"] or "General",
                    "page_number": int(r["page_number"]) if r["page_number"] else 1,
                    "text_content": r["text_content"],
                }
                # Enrich text with title and doc name for high lexical matching sensitivity
                rich_text = f"{chunk_dict['document_name']} {chunk_dict['section_title']} {chunk_dict['text_content']}"
                tokens = tokenize_text(rich_text)
                corpus_tokens.append(tokens)
                chunks.append(chunk_dict)

            bm25 = BM25Okapi(corpus_tokens)
            index_data = {
                "bm25": bm25,
                "chunks": chunks,
                "total_chunks": len(chunks)
            }
            self._version_indices[product_version] = index_data
            logger.info(f"Built BM25 index for '{product_version}' over {len(chunks)} chunks.")
            return index_data

        except Exception as e:
            logger.error(f"Error building BM25 index for version {product_version}: {e}")
            return None

    def search(
        self,
        query: str,
        product_version: str,
        top_k: int = 4,
        document_type: Optional[str] = None,
        document_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute BM25 keyword search isolated strictly to the specified product version.
        Returns a ranked list of candidate chunks with normalized sparse scores.
        """
        index_data = self._version_indices.get(product_version)
        if index_data is None:
            index_data = self._build_version_index(product_version)

        if not index_data or not index_data["chunks"]:
            return []

        query_tokens = tokenize_text(query)
        if not query_tokens:
            return []

        bm25: BM25Okapi = index_data["bm25"]
        chunks: List[Dict[str, Any]] = index_data["chunks"]

        # Compute raw BM25 scores
        raw_scores = bm25.get_scores(query_tokens)

        # Pair chunks with scores
        scored_candidates: List[Dict[str, Any]] = []
        for chunk, score in zip(chunks, raw_scores):
            # Optional metadata filter
            if document_type and chunk["document_type"].lower() != document_type.lower():
                continue
            if document_name and chunk["document_name"].lower() != document_name.lower():
                continue

            if score > 0.0:
                scored_candidates.append({
                    "chunk": chunk,
                    "raw_score": float(score)
                })

        if not scored_candidates:
            return []

        # Sort descending by raw score
        scored_candidates.sort(key=lambda x: x["raw_score"], reverse=True)

        # Normalize score to [0, 1] relative to the top scoring candidate
        max_score = scored_candidates[0]["raw_score"]
        results: List[Dict[str, Any]] = []

        for rank, item in enumerate(scored_candidates[:top_k], start=1):
            chunk = item["chunk"]
            normalized_score = item["raw_score"] / max_score if max_score > 0 else 0.0

            results.append({
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "document_name": chunk["document_name"],
                "product_name": chunk["product_name"],
                "product_version": chunk["product_version"],
                "document_type": chunk["document_type"],
                "section_title": chunk["section_title"],
                "page_number": chunk["page_number"],
                "text_content": chunk["text_content"],
                "sparse_score": round(normalized_score, 4),
                "raw_bm25_score": round(item["raw_score"], 4),
                "rank": rank,
                "retrieval_method": "bm25",
                "metadata": {
                    "document_id": chunk["document_id"],
                    "document_name": chunk["document_name"],
                    "product_name": chunk["product_name"],
                    "product_version": chunk["product_version"],
                    "document_type": chunk["document_type"],
                    "section_title": chunk["section_title"],
                    "page_number": chunk["page_number"],
                }
            })

        return results


# Global instance
bm25_retriever = BM25Retriever()
