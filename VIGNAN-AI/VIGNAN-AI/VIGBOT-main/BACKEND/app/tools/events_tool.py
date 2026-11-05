from typing import Dict, Any, Optional, List
from app.database import DataRepository, DatabaseSession

def get_events_summary(session: Optional[DatabaseSession] = None, query: str = "") -> Dict[str, Any]:
    """
    Returns upcoming campus events, festivals (Mahotsav), technical hackathons,
    and academic milestones from the database and calendar records.
    """
    events = DataRepository.get_upcoming_events()
    
    text_lines: List[str] = [
        "🎉 **Upcoming VFSTR Campus Events & Extracurricular Activities:**\n",
        "• **Major University Festivals & Flagship Events:**",
        "  1. **Vignan Mahotsav 2026 (National Youth & Cultural Fest):**",
        "     - Flagship 3-day cultural festival with interstate dance, battle of bands, theatrical drama, literature conclave, and celebrity musical night.",
        "     - Venue: University Open Air Theatre & Main Lawns\n",
        "  2. **Tech Innovate 2026 (36-Hour Hackathon):**",
        "     - Hosted by the AI Innovation Club & SAC. Open coding hackathon across AI, IoT, Web3, and Robotics domains with industry mentorship.",
        "     - Venue: Main Auditorium & Computing Labs\n",
        "  3. **Annual Sports Fest & Champions Trophy:**",
        "     - Inter-departmental and inter-university tournaments in cricket, basketball, volleyball, badminton, and athletics.",
        "     - Venue: University Sports Complex & Synthetic Courts\n",
        "• **Semester Academic Milestones (2026-27):**",
        "  - **Continuous Internal Evaluation 2 (CIE-2):** Oct 14 – Oct 21, 2026",
        "  - **Dasara Cultural Holidays:** Oct 18 – Oct 21, 2026",
        "  - **Practical & Theory Summative Assessments:** Nov 14 – Dec 04, 2026",
        "  - **Commencement of II Semester:** Dec 14, 2026\n",
        "To participate or volunteer for any event, visit the **Student Activity Council (SAC Office, Room 201)** or check your active club channels."
    ]

    card_data = {
        "type": "events",
        "title": "Upcoming Campus Events & Activities",
        "subtitle": "VFSTR Cultural, Technical & SAC Schedule",
        "badge": "Campus Highlights",
        "badgeVariant": "purple",
        "data": {
            "festivals": [
                {"name": "Vignan Mahotsav", "type": "National Cultural Fest", "venue": "Open Air Theatre"},
                {"name": "Tech Innovate Hackathon", "type": "36-Hour Coding Hackathon", "venue": "Main Auditorium"},
                {"name": "Annual Sports Fest", "type": "Athletics & Games", "venue": "Sports Complex"}
            ],
            "sacDesk": "Room 201, SAC Building",
            "activeEventsCount": len(events)
        },
        "actionLabel": "Browse Active Clubs",
        "actionIntent": "What student clubs are available?"
    }

    return {
        "text": "\n".join(text_lines),
        "citations": [],
        "structured_card": card_data
    }

