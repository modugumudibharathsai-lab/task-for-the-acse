from typing import Dict, Any, Optional, List
from app.database import DataRepository, DatabaseSession

def get_transport_summary(session: Optional[DatabaseSession] = None, query: str = "") -> Dict[str, Any]:
    """
    Returns grounded VFSTR college bus routes (Guntur, Vijayawada, Tenali),
    bus pass renewal procedure, and transport office contacts.
    """
    db_routes = DataRepository.get_transport_routes()
    
    text_lines: List[str] = [
        "🚌 **VFSTR College Bus Fleet & Campus Transit System:**\n",
        "• **Major Bus Transit Routes:**",
        "  1. **Route 1 (Guntur City Express):**",
        "     - Stoppages: Guntur Bus Stand → Gujjanagundla → Vidyanagar → Collector Office → VFSTR Campus.",
        "     - Arrival: 7:35 AM | Evening Return: 4:45 PM\n",
        "  2. **Route 2 (Vijayawada City Express):**",
        "     - Stoppages: Benz Circle → Auto Nagar → Poranki → Kankipadu → Tenali Bridge → VFSTR Campus.",
        "     - Arrival: 7:30 AM | Evening Return: 4:45 PM\n",
        "  3. **Route 3 (Tenali Town Shuttle):**",
        "     - Stoppages: Tenali Railway Station → Chenchupet → Morrispet → Nandivelugu → VFSTR Campus.",
        "     - Arrival: 7:40 AM | Evening Return: 4:45 PM\n",
        "  4. **Route 4 (Weekend Rail Link):**",
        "     - Dedicated transit link connecting hostel boarders to Tenali & Guntur railway stations on Saturday/Sunday evenings.\n",
        "• **Bus Pass Endorsement & Renewal Procedure:**",
        "  1. Pay the transport fee before the semester commencement date.",
        "  2. Bring your payment receipt and student identity card to the **Transport Desk (Admin Block, Room G-08)**.",
        "  3. An RFID bus pass sticker will be endorsed for the semester.\n",
        "• **Transport Office Contacts:**",
        "  - **Transport Desk:** Room G-08, Admin Block Ground Floor",
        "  - **Helpline:** +91-863-2344755 / +91-98481-99887",
        "  - **Email:** `transport@vignan.ac.in`",
    ]

    card_data = {
        "type": "transport",
        "title": "VFSTR College Bus & Transit Services",
        "subtitle": "Guntur, Vijayawada & Tenali Routes",
        "badge": "Active Fleet",
        "badgeVariant": "green",
        "data": {
            "routes": [
                "Route 1: Guntur Express (Bus Stand - Vidyanagar)",
                "Route 2: Vijayawada City (Benz Circle - Poranki)",
                "Route 3: Tenali Town (Station - Morrispet)",
                "Route 4: Weekend Railway Station Link"
            ],
            "deskLocation": "Admin Block Room G-08 (Transport Desk)",
            "contact": "+91-863-2344755 / transport@vignan.ac.in",
            "endorsement": "Payment Receipt + Student ID at Room G-08"
        },
        "actionLabel": "Request Bus Pass",
        "actionIntent": "Submit a service request for bus pass endorsement"
    }

    citations = [
        {
            "title": "Campus Discipline & Vehicular Regulations",
            "clause": "Clause CD-04",
            "effective_date": "2024-01-10",
            "summary": "Mandates college bus RFID pass display and traffic regulations on campus."
        }
    ]

    return {
        "text": "\n".join(text_lines),
        "citations": citations,
        "structured_card": card_data
    }

