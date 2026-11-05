from typing import Dict, Any, List
from app.database import DataRepository
from app.research.vignan_rag import get_vignan_retriever

def search_policies_and_circulars(query: str) -> Dict[str, Any]:
    normalized_query = query.lower()
    asks_for_circulars = any(term in normalized_query for term in ("circular", "notice", "notification"))
    asks_for_policies = any(term in normalized_query for term in ("policy", "policies", "regulation", "regulations", "bylaw", "ordinance", "rule"))

    # 1. SQL policies and circulars
    policies = DataRepository.search_policies(query) if asks_for_policies or not asks_for_circulars else []
    circulars = DataRepository.search_circulars(query) if asks_for_circulars or not asks_for_policies else []
    
    citations = []
    text_lines = []

    if policies:
        text_lines.append("📜 **Approved Institutional Regulations & Policies:**")
        for p in policies:
            text_lines.append(f"\n• **{p['title']}** ({p['clause_no']}) - Effective: {p['effective_date']}")
            text_lines.append(f"  \"{p['summary']}\"")
            text_lines.append(f"  *Authority: {p['authority']}*")
            citations.append({
                "title": p["title"],
                "clause": p["clause_no"],
                "effective_date": p["effective_date"],
                "summary": p["summary"],
                "url": "https://vignan.ac.in/newvignan/Regulations.php"
            })

    if circulars:
        text_lines.append("\n📢 **Official Circulars & Notices:**")
        for c in circulars:
            text_lines.append(f"\n• **{c['title']}** (Ref: {c['circular_no']}) - Issued: {c['issued_date']}")
            text_lines.append(f"  \"{c['summary']}\"")
            text_lines.append(f"  *Issued by: {c['issued_by']}*")
            citations.append({
                "title": c["title"],
                "clause": c["circular_no"],
                "effective_date": c["effective_date"],
                "summary": c["summary"],
                "url": "https://vignan.ac.in/newvignan/vfstrmanual_index.php"
            })

    # 2. Hybrid RAG Knowledge Base Retrieval
    try:
        rag_retriever = get_vignan_retriever()
        rag_chunks = rag_retriever.retrieve(query, top_k=2)
        if rag_chunks:
            text_lines.append("\n🏛️ **Official Vignan University Knowledge & Guidelines:**")
            for chunk in rag_chunks:
                text_lines.append(f"\n• **{chunk['title']}** ({chunk['clause_no']})")
                text_lines.append(f"  \"{chunk['text']}\"")
                text_lines.append(f"  *Source: {chunk['source_url']}*")
                citations.append({
                    "title": chunk["title"],
                    "clause": chunk["clause_no"],
                    "effective_date": chunk["effective_date"],
                    "summary": chunk["text"][:150] + "...",
                    "url": chunk["source_url"]
                })
    except Exception:
        pass

    card_data = {
        "type": "policy",
        "title": "Official Institutional Regulations & Circulars",
        "subtitle": f"{len(citations)} Official Citations Found",
        "badge": "Approved Knowledge",
        "badgeVariant": "blue",
        "data": {
            "citations": citations
        }
    }

    return {
        "text": "\n".join(text_lines),
        "citations": citations,
        "structured_card": card_data
    }
