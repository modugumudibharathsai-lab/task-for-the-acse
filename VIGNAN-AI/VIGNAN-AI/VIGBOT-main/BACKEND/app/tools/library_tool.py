from typing import Dict, Any, Optional
from app.database import DataRepository, DatabaseSession
import datetime

def get_library_summary(session: DatabaseSession) -> Dict[str, Any]:
    records = DataRepository.get_library_lended_books(session)
    if not records:
        return {
            "text": "There are no library records or issued books associated with your student profile in the database.",
            "has_records": False
        }

    # Format the response
    overdue_books = []
    issued_books = []

    now = datetime.datetime.now()

    for rec in records:
        try:
            due_date = datetime.datetime.fromisoformat(rec["due_date"])
            if now > due_date and rec["status"] != "Returned":
                rec["status"] = "Overdue"
        except:
            pass
            
        if rec["status"].lower() == "overdue":
            overdue_books.append(rec)
        else:
            issued_books.append(rec)

    text_lines = ["Here are your library records:\n"]
    
    if overdue_books:
        text_lines.append("⚠️ **OVERDUE BOOKS:**")
        for b in overdue_books:
            # Reformat isoformat to a nice string if possible
            due_str = b["due_date"][:10]
            text_lines.append(f"• **{b['book_title']}** (Due: {due_str}) - Please return immediately.")
        text_lines.append("")

    if issued_books:
        text_lines.append("📖 **ISSUED BOOKS:**")
        for b in issued_books:
            due_str = b["due_date"][:10]
            text_lines.append(f"• **{b['book_title']}** (Due: {due_str})")

    text = "\n".join(text_lines)

    # We can create a simple card for the first overdue book or first issued book
    card_title = "Central Library Books"
    badge_variant = "amber" if overdue_books else "blue"
    subtitle = f"{len(overdue_books)} Overdue, {len(issued_books)} Issued"

    card_data = {
        "type": "library",
        "title": card_title,
        "subtitle": subtitle,
        "badge": "Overdue" if overdue_books else "Clear",
        "badgeVariant": badge_variant,
        "data": {
            "Total Issued": len(records),
            "Overdue": len(overdue_books),
            "Returned": 0
        },
        "actionLabel": "View All Books"
    }

    return {
        "text": text,
        "records": records,
        "structured_card": card_data
    }
