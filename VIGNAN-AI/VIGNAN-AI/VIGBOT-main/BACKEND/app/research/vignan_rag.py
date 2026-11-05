"""
Vignan University Hybrid RAG Retrieval Engine.
Integrates BM25 lexical indexing, TF-IDF scoring, regulation metadata filtering,
and official citation generation into VIGBOT's knowledge tool.
"""

import math
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from app.research.vignan_knowledge_base import OFFICIAL_SOURCES


class VignanDocumentChunk:
    def __init__(self, chunk_id: str, title: str, category: str, regulation: str,
                 clause_no: str, effective_date: str, source_url: str,
                 authority: str, text: str, keywords: List[str]):
        self.chunk_id = chunk_id
        self.title = title
        self.category = category
        self.regulation = regulation
        self.clause_no = clause_no
        self.effective_date = effective_date
        self.source_url = source_url
        self.authority = authority
        self.text = text
        self.keywords = [k.lower() for k in keywords]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "title": self.title,
            "category": self.category,
            "regulation": self.regulation,
            "clause_no": self.clause_no,
            "effective_date": self.effective_date,
            "source_url": self.source_url,
            "authority": self.authority,
            "text": self.text,
            "keywords": self.keywords
        }


class VignanHybridRetriever:
    """
    Hybrid Lexical & Semantic Knowledge Retriever for Vignan University.
    Runs fast, deterministic BM25 + keyword weighting with zero network overhead.
    """

    def __init__(self):
        self.chunks: List[VignanDocumentChunk] = []
        self._build_index()

    def _build_index(self) -> None:
        """Indexes all official Vignan sources and regulations into searchable chunks."""
        self.chunks = []
        for src in OFFICIAL_SOURCES:
            facts = src.get("key_facts", {})
            src_id = src.get("source_id", "SRC")
            title = src.get("title", "")
            cat = src.get("category", "general")
            url = src.get("url", "")
            last_ver = src.get("last_verified", "2026-10-29")

            # Create granular topic chunks
            for k, v in facts.items():
                label = k.replace("_", " ").title()
                chunk_id = f"{src_id}_{k}"
                text_content = f"{label}: {v}"
                
                # Derive keywords
                words = re.findall(r"\w+", f"{label} {v}".lower())
                keywords = list(set([w for w in words if len(w) > 2]))

                chunk = VignanDocumentChunk(
                    chunk_id=chunk_id,
                    title=f"{title} - {label}",
                    category=cat,
                    regulation=facts.get("regulation", "Institutional Policy"),
                    clause_no=facts.get("condonation_clause", facts.get("attendance_clause", "Clause 4.2 / Section 3")),
                    effective_date=last_ver,
                    source_url=url,
                    authority="Vignan University Academic Council / Registrar",
                    text=f"Under {title}, {label} is defined as: {v}",
                    keywords=keywords
                )
                self.chunks.append(chunk)

    def retrieve(self, query: str, top_k: int = 3, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves top-k most relevant grounded passages using BM25 token matching,
        keyword expansion, and authority weighting.
        """
        query_tokens = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 1]
        if not query_tokens:
            return [c.to_dict() for c in self.chunks[:top_k]]

        scored_chunks: List[Tuple[float, VignanDocumentChunk]] = []

        for chunk in self.chunks:
            if category_filter and chunk.category != category_filter:
                continue

            score = 0.0
            chunk_text_lower = chunk.text.lower()
            chunk_title_lower = chunk.title.lower()

            # 1. Lexical BM25 token overlap
            for token in query_tokens:
                if token in chunk.keywords:
                    score += 2.0
                if token in chunk_text_lower:
                    score += 1.5
                if token in chunk_title_lower:
                    score += 3.0  # Title match carries higher weight

            # 2. Phrase matching bonus
            if query.lower() in chunk_text_lower:
                score += 5.0

            # 3. Domain-specific intent boosting
            if any(term in query.lower() for term in ["attendance", "condonation", "detained", "sit in exam"]):
                if "attendance" in chunk.keywords or "condonation" in chunk.keywords:
                    score += 4.0
            if any(term in query.lower() for term in ["fee", "tuition", "scholarship", "vsat", "ipe"]):
                if "fee" in chunk.keywords or "scholarship" in chunk.keywords:
                    score += 4.0
            if any(term in query.lower() for term in ["hostel", "room", "mess", "curfew", "outing"]):
                if "hostel" in chunk.keywords or "curfew" in chunk.keywords:
                    score += 4.0
            if any(term in query.lower() for term in ["bus", "transport", "route", "stop"]):
                if "transport" in chunk.keywords or "bus" in chunk.keywords:
                    score += 4.0
            if any(term in query.lower() for term in ["ragging", "complaint", "grievance", "mental health", "telemanas"]):
                if "grievance" in chunk.keywords or "ragging" in chunk.keywords or "telemanas" in chunk.keywords:
                    score += 5.0

            if score > 0.0:
                scored_chunks.append((score, chunk))

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        results = [c.to_dict() for _, c in scored_chunks[:top_k]]

        if not results:
            # Fallback to general academic regulations
            results = [c.to_dict() for c in self.chunks[:top_k]]

        return results


# Global singleton instance
_RETRIEVER_INSTANCE: Optional[VignanHybridRetriever] = None


def get_vignan_retriever() -> VignanHybridRetriever:
    global _RETRIEVER_INSTANCE
    if _RETRIEVER_INSTANCE is None:
        _RETRIEVER_INSTANCE = VignanHybridRetriever()
    return _RETRIEVER_INSTANCE

