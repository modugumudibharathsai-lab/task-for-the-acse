from typing import Dict, Any, Optional, List
from app.database import DataRepository, DatabaseSession

def get_circulars_summary(session: Optional[DatabaseSession] = None, query: str = "") -> Dict[str, Any]:
    """
    Queries and returns official circulars and notices from the circulars database table.
    """
    circulars = DataRepository.get_all_circulars()
    citations: List[Dict[str, Any]] = []
    text_lines: List[str] = [
        "📢 **Official Institutional Circulars & Administrative Notices:**\n"
    ]

    for c in circulars:
        text_lines.append(f"• **{c['title']}** (Ref: `{c['circular_no']}`)")
        text_lines.append(f"  - **Issued Date:** {c.get('issued_date')} | **Effective:** {c.get('effective_date', 'Immediate')}")
        text_lines.append(f"  - **Summary:** \"{c['summary']}\"")
        text_lines.append(f"  - *Issued by: {c.get('issued_by', 'Office of the Registrar')}*\n")
        citations.append({
            "title": c["title"],
            "clause": c["circular_no"],
            "effective_date": c.get("effective_date", c.get("issued_date")),
            "summary": c["summary"]
        })

    text_lines.append("Students can view the complete repository of signed administrative orders in the **Circulars** tab or on the university notice board.")

    card_data = {
        "type": "circulars",
        "title": "Official Institutional Circulars & Notifications",
        "subtitle": f"{len(circulars)} Published Senate & Registrar Notices",
        "badge": "Official Notices",
        "badgeVariant": "blue",
        "data": {
            "circularCount": len(circulars),
            "latestNotices": [
                {"ref": c["circular_no"], "title": c["title"], "date": c.get("issued_date")}
                for c in circulars[:3]
            ]
        },
        "actionLabel": "View Academic Calendar",
        "actionIntent": "When is the next academic holiday?"
    }

    return {
        "text": "\n".join(text_lines),
        "citations": citations,
        "structured_card": card_data
    }

