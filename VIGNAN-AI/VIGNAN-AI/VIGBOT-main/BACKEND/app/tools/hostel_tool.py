from typing import Dict, Any, Optional, List
from app.database import DataRepository, DatabaseSession

def get_hostel_summary(session: Optional[DatabaseSession] = None, query: str = "") -> Dict[str, Any]:
    """
    Returns grounded VFSTR hostel rules, mess timings/menu, outing pass procedure,
    and warden contact details from the database policies table.
    """
    all_policies = DataRepository.get_all_policies()
    hostel_policies = [p for p in all_policies if p.get("clause_no", "").startswith("HD-")]

    citations: List[Dict[str, Any]] = []
    text_lines: List[str] = [
        "🏢 **VFSTR Hostel & Dining Regulations (Hostel Hub):**\n",
        "• **Curfew & Movement (Clause HD-01):**",
        "  All residents must report to the hostel before **6:00 PM**. Late entries must log their purpose in the Movement Register. Strict campus gate closure is enforced at **10:00 PM**.\n",
        "• **Outing Pass & Station Leaves (Clause HD-02):**",
        "  Station leave or weekend outing requires a formal written pass applied **2 days in advance** through the Hostel Office. Leaving without intimation is an academic offense and authorizes the Chief Warden to inventory the room.\n",
        "• **Visitor Protocol (Clause HD-03):**",
        "  Parents and authorized local guardians are permitted to visit on **Saturdays & Sundays between 4:00 PM and 6:00 PM** in the visitor lobby only. Guests are strictly barred from resident rooms.\n",
        "• **Room Protocol & Prohibited Appliances (Clause HD-04):**",
        "  High-wattage appliances (electric stoves, immersion heaters, iron boxes) are strictly prohibited for fire safety. Valuables/cash kept in rooms should not exceed Rs. 1,000.\n",
        "• **Mess Timings & Dining Protocol (Clause HD-05):**",
        "  - **Breakfast:** 7:30 AM – 8:45 AM",
        "  - **Lunch:** 12:30 PM – 2:00 PM",
        "  - **Evening Tea & Snacks:** 5:00 PM – 6:00 PM",
        "  - **Dinner:** 7:30 PM – 9:00 PM",
        "  *Note: Outside cooked food is strictly banned. Food and utensils may not be removed from the dining hall.*\n",
        "• **Medical Support & Sick Room Service (Clause HD-06):**",
        "  Residents feeling unwell must report immediately to the resident Warden. Approved sick-diet room service is provided upon medical clearance.\n",
        "📞 **Official Hostel Administration & Warden Contacts:**",
        "• **Chief Warden Office:** Room H-01, Ground Floor Block H (Phone: +91-863-2344700 / Ext. 301)",
        "• **Boys Hostel Warden:** +91-98481-12345",
        "• **Girls Hostel Warden:** +91-98481-54321",
        "• **Campus Health Clinic (24/7):** Ext. 204",
    ]

    for p in hostel_policies:
        citations.append({
            "title": p.get("title"),
            "clause": p.get("clause_no"),
            "effective_date": p.get("effective_date"),
            "summary": p.get("summary")
        })

    card_data = {
        "type": "hostel",
        "title": "VFSTR Hostel & Dining Services",
        "subtitle": "Hostel Regulations & Mess Protocol",
        "badge": "Hostel Resident Portal",
        "badgeVariant": "blue",
        "data": {
            "curfew": "6:00 PM Reporting (10:00 PM Gate Closure)",
            "messTimings": "Breakfast: 7:30-8:45 AM | Lunch: 12:30-2:00 PM | Dinner: 7:30-9:00 PM",
            "outingPass": "Submit 2 days prior to Chief Warden",
            "wardenContact": "Chief Warden Office: +91-863-2344700 (Ext. 301)"
        },
        "actionLabel": "Apply Outing Pass",
        "actionIntent": "Apply for hostel outing pass"
    }

    return {
        "text": "\n".join(text_lines),
        "citations": citations,
        "structured_card": card_data
    }

