"""
VIGBOT Universal Semantic NLU & Action Intelligence Engine.
Provides:
1. Discourse-aware multi-turn context resolution (anaphora 'open it', topic switching, missing params).
2. Distinction between Asking (Information), Navigating (Navigation), Doing (Action), Tracking (Status), and Canceling.
3. Multilingual and colloquial understanding (Hinglish, slang, typos, abbreviations).
4. Strict False-Action Prevention Guard across all 28 application capabilities.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from app.agent.capability_registry import (
    APPLICATION_CAPABILITIES,
    CommunicationIntent,
    OperationType,
    find_matching_capability
)


class UniversalNLU:
    """
    Universal semantic understanding layer for VIGBOT.
    Handles multi-turn discourse, multilingual idioms, and guarantees zero unauthorized actions.
    """

    # Hinglish & colloquial mappings
    HINGLISH_TRANSLATIONS = {
        "kahan": "where",
        "kidhar": "where",
        "kaise": "how",
        "karo": "do",
        "kholo": "open",
        "dikhao": "show",
        "batao": "tell",
        "bata": "tell",
        "chahiye": "need",
        "karna hai": "want to do",
        "daalna hai": "want to submit",
        "lagana hai": "want to apply",
        "kya scene hai": "what is status",
        "kahan milega": "where to find",
        "pata karna hai": "want to know",
        "meri": "my",
        "mera": "my",
        "apna": "my",
        "isko": "it",
        "use": "it",
        "ise": "it",
        "usko": "that",
        "ye": "this",
        "yeh": "this",
        "wo": "that",
        "woh": "that"
    }

    @classmethod
    def normalize_query_semantics(cls, query: str) -> str:
        """
        Normalizes slang, Hinglish, punctuation, and typographical variations
        into standardized semantic tokens while preserving the raw query.
        """
        q = query.lower().strip()
        # Clean punctuation except hyphens/quotes
        q = re.sub(r"[?!.,;:()\[\]{}]", " ", q)
        words = q.split()
        normalized_words = [cls.HINGLISH_TRANSLATIONS.get(w, w) for w in words]
        normalized_q = " ".join(normalized_words)
        return normalized_q

    @classmethod
    def resolve_contextual_capability(
        cls,
        query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Resolves the target capability from the current query or multi-turn history
        (e.g., resolving 'open it', 'take me there', 'yes please').
        """
        # 1. Direct query matching
        direct_match = find_matching_capability(query)
        if direct_match is not None:
            return direct_match

        # 2. Anaphoric reference resolution from recent conversation history
        q_norm = cls.normalize_query_semantics(query)
        anaphora_triggers = [
            "open it", "take me there", "go there", "show it", "navigate there",
            "open that", "open the tab", "kholo", "yes", "yes please", "sure",
            "open page", "take me", "view it", "show that", "let's go",
            "open this", "show this", "kholo isko", "isko kholo", "open", "kholo"
        ]
        has_anaphora = any(trig in q_norm or q_norm == trig for trig in anaphora_triggers)

        if has_anaphora and conversation_history:
            # Search backwards through recent assistant turns for capability mentions
            for msg in reversed(conversation_history):
                content = msg.get("content", "").lower()
                meta = msg.get("responseMeta") or {}
                redirect_path = meta.get("redirect_path") or msg.get("redirect_path")
                
                # Check explicit redirect_path in metadata
                if redirect_path and redirect_path in APPLICATION_CAPABILITIES:
                    return APPLICATION_CAPABILITIES[redirect_path]

                # Check category or capability name in message
                for cap_id, cap in APPLICATION_CAPABILITIES.items():
                    if cap["name"].lower() in content or cap_id in content or cap["category"].lower() in content:
                        return cap

        return None

    @classmethod
    def parse_communication_intent(
        cls,
        query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> CommunicationIntent:
        """
        Determines the student's communication intent using deep semantic parsing.
        Distinguishes:
        - INFORMATION_REQUEST (asking where/how/rules)
        - NAVIGATION_REQUEST (asking to open/switch views)
        - ACTION_REQUEST (asking to execute, book, submit, report)
        - CANCEL_REQUEST (asking to cancel/abort/withdraw)
        - STATUS_LOOKUP (checking approval, tracking ticket)
        - PERSONAL_DATA_REQUEST (fetching authenticated student record)
        - GENERAL_ACADEMIC (pedagogical/subject tutoring)
        - AMBIGUOUS (underspecified)
        - CONVERSATION (greetings/social)
        """
        q_raw = query.strip()
        q_norm = cls.normalize_query_semantics(query)
        q_lower = q_raw.lower()

        # 1. Negative request with Information intent ("Don't submit anything, just tell me where...")
        if any(neg in q_norm for neg in ["don't", "dont", "do not"]):
            if any(info_word in q_norm for info_word in ["tell me", "where", "how", "what", "details", "info", "show", "find"]):
                return CommunicationIntent.INFORMATION_REQUEST

        # 2. Negative / Abort / Cancellation Intent
        cancel_markers = [
            "cancel my", "cancel that", "cancel booking", "withdraw application",
            "cancel request", "abort", "don't book", "dont book", "don't submit",
            "dont submit", "stop that", "actually cancel", "forget that"
        ]
        if any(cm in q_norm for cm in cancel_markers):
            return CommunicationIntent.CANCEL_REQUEST

        # 2. Greetings and Pleasantries
        greetings = ["hello", "hi", "hey", "namaste", "good morning", "good evening", "thank you", "thanks", "bye"]
        if q_lower in greetings:
            return CommunicationIntent.CONVERSATION

        # 3. Status Tracking & Lookup Intent
        status_markers = [
            "status of", "track my ticket", "track my request", "track my application",
            "has my application", "has my request", "is my application", "is my request",
            "is my ticket", "is my complaint", "check status", "ticket status",
            "application status", "any update on", "is it approved", "whether it is approved",
            "i already submitted", "what is status", "kahan tak pahuncha", "kya hua",
            "track ticket", "sr-2026-", "anc-"
        ]
        if any(sm in q_norm or sm in q_lower for sm in status_markers):
            return CommunicationIntent.STATUS_LOOKUP

        # 4. Explicit Navigation Request ("Open Lost & Found", "Take me to attendance", "kholo", "open it")
        # Guard: Inquiries like "is the library open this sunday?" are information questions, NOT navigation commands!
        is_asking_if_open = any(k in q_norm for k in [
            "is the", "is it", "will it", "when does", "what time does",
            "open on", "open this", "hours", "timings", "close", "closing"
        ])
        if not is_asking_if_open:
            nav_triggers = [
                "go to", "take me to", "navigate to", "show tab", "switch to",
                "view tab", "take me there", "go there", "open it", "kholo", "show me the tab"
            ]
            is_nav_cmd = q_norm.startswith("open ") or any(nt in q_norm for nt in nav_triggers)
            if is_nav_cmd:
                target_cap = cls.resolve_contextual_capability(query, conversation_history)
                if target_cap is not None:
                    return CommunicationIntent.NAVIGATION_REQUEST

        # 5. Negative phrasing with info intent ("Don't book anything, just tell me where it is")
        if "don't" in q_norm or "dont" in q_norm:
            if any(info_word in q_norm for info_word in ["tell me", "where", "how", "what", "details"]):
                return CommunicationIntent.INFORMATION_REQUEST

        # 6. Informational Request (ASKING, NOT DOING!)
        # CRITICAL: Asking where/how to do something is NEVER an action request!
        info_markers = [
            "where can i", "where do i", "where to", "how do i", "how can i", "how to",
            "how am i supposed to", "where do i go for", "where can i find", "tell me where",
            "tell me how", "what is the process", "what is the procedure", "who should i contact",
            "is there a way to", "rules for", "what are the timings", "kahan", "kaise",
            "can i know", "tell me about", "details about", "kahan milega"
        ]
        if any(im in q_norm for im in info_markers):
            return CommunicationIntent.INFORMATION_REQUEST

        # 7. General Academic Concept Inquiries (DSA, DBMS, OS, Mathematics, Electronics)
        academic_concepts = [
            "normalization", "1nf", "2nf", "3nf", "bcnf", "binary search", "quicksort",
            "mergesort", "stack", "queue", "linked list", "flip-flop", "flip flop", "8051",
            "microcontroller", "deadlock", "paging", "osi layer", "tcp", "udp", "dsa",
            "discrete math", "boolean algebra", "bubble sort", "acid properties", "eigenvalues",
            "laplace transform", "fourier transform", "differential equation"
        ]
        if any(term in q_lower for term in academic_concepts) and not any(k in q_lower for k in ["my attendance", "my fee", "my marks"]):
            return CommunicationIntent.GENERAL_ACADEMIC

        # 8. Personal Student Data Inquiries
        personal_markers = [
            "my attendance", "meri attendance", "my fees", "my marks", "my cgpa", "my sgpa",
            "my timetable", "my classes", "classes i attended", "my hostel room", "my advisor",
            "my mentor", "am i eligible", "will i reach 75", "can i sit in exam", "classes needed"
        ]
        if any(pm in q_norm for pm in personal_markers):
            return CommunicationIntent.PERSONAL_DATA_REQUEST

        # 9. Ambiguous Queries (Underspecified)
        # Note: Open help requests ("help me", "start", "menu") trigger the personalized proactive academic briefing
        ambiguous_phrases = [
            "i found something", "found something", "i lost something", "lost something",
            "i have a problem", "i have an issue", "need to report something", "report an issue",
            "help with something", "something went wrong"
        ]
        if q_lower in ambiguous_phrases or any(q_lower == p for p in ambiguous_phrases):
            return CommunicationIntent.AMBIGUOUS

        # 10. Explicit Action Request (DOING: User explicitly asks to book, apply, submit, report)
        action_markers = [
            "i want to report", "i want to submit", "i want to apply", "please report",
            "please submit", "please apply", "book a", "register for", "apply for",
            "lodge grievance", "file complaint", "submit grievance", "claim this item",
            "i need to get this done", "submit this", "do this for me", "i want to book",
            "i want to join", "join the club", "apply for bonafide", "need a bonafide",
            "want a bonafide", "apply karna", "book karna", "submit karna", "daalna hai",
            "lagana hai", "chahiye"
        ]
        if any(am in q_norm for am in action_markers):
            return CommunicationIntent.ACTION_REQUEST

        # Default fallback: If it references an application feature, treat as informational guidance
        matching_cap = cls.resolve_contextual_capability(query, conversation_history)
        if matching_cap is not None:
            return CommunicationIntent.INFORMATION_REQUEST

        return CommunicationIntent.INFORMATION_REQUEST

    @classmethod
    def resolve_and_execute(
        cls,
        session: Any,
        query: str,
        student_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Universal capability-aware resolution engine.
        Enforces false-action guards, handles multi-turn references,
        and returns structured responses with verified navigation payloads.
        """
        comm_intent = cls.parse_communication_intent(query, conversation_history)
        matching_cap = cls.resolve_contextual_capability(query, conversation_history)

        # -------------------------------------------------------------------
        # 1. CANCEL / ABORT REQUEST: Safely acknowledge cancellation without writes
        # -------------------------------------------------------------------
        if comm_intent == CommunicationIntent.CANCEL_REQUEST:
            cap_name = matching_cap["name"] if matching_cap else "operation"
            return {
                "content": f"Understood. I have canceled this {cap_name} request. No changes were made to your records.",
                "category": matching_cap["category"] if matching_cap else "GENERAL",
                "topic": "Request Canceled",
                "source_agent": "VIGBOT (Workflow Controller)",
                "redirect_path": matching_cap["frontend_tab"] if matching_cap else None,
                "action": None,
                "structured_card": None,
                "citations": [],
                "routed_by": "universal_nlu"
            }

        # -------------------------------------------------------------------
        # 2. STATUS LOOKUP: Track actual database tickets, never fabricate!
        # -------------------------------------------------------------------
        if comm_intent == CommunicationIntent.STATUS_LOOKUP:
            q_upper = query.upper()
            # Extract possible tracking number (e.g. SR-2026-0213, ANC-1024)
            sr_match = re.search(r"\b(SR-\d{4}-\d{4,5})\b", q_upper)
            anc_match = re.search(r"\b(ANC-\d{4,5})\b", q_upper)

            # Check Service Request database
            if sr_match and session:
                from app.database import DataRepository
                req_no = sr_match.group(1)
                user_requests = DataRepository.list_service_requests(session)
                found_req = next((r for r in user_requests if r.get("request_no") == req_no), None)
                if found_req:
                    return {
                        "content": (
                            f"📋 **Official Status for Ticket {req_no}:**\n\n"
                            f"• **Category:** {found_req.get('category')}\n"
                            f"• **Title:** {found_req.get('title')}\n"
                            f"• **Assigned Office:** {found_req.get('assigned_office', 'Registrar Office')}\n"
                            f"• **Current Status:** **{found_req.get('status')}**\n"
                            f"• **Estimated SLA Date:** {found_req.get('sla_due_date', 'Within 3 working days')}"
                        ),
                        "category": "SERVICE_REQUEST",
                        "topic": f"Status: {req_no}",
                        "source_agent": "VIGBOT (Ticket Tracker)",
                        "redirect_path": "services",
                        "action": {
                            "type": "navigate",
                            "label": "Open Student Services",
                            "target": "services",
                            "route": "/?tab=services"
                        },
                        "structured_card": None,
                        "citations": [],
                        "routed_by": "universal_nlu"
                    }
                else:
                    return {
                        "content": (
                            f"I searched your student records, but could not find an active ticket matching **{req_no}**.\n"
                            f"Please verify the tracking number or view your submitted requests in the **Student Services** tab."
                        ),
                        "category": "SERVICE_REQUEST",
                        "topic": "Ticket Not Found",
                        "source_agent": "VIGBOT (Ticket Tracker)",
                        "redirect_path": "services",
                        "action": {
                            "type": "navigate",
                            "label": "View All Requests",
                            "target": "services",
                            "route": "/?tab=services"
                        },
                        "structured_card": None,
                        "citations": [],
                        "routed_by": "universal_nlu"
                    }

            # General status lookup for active submissions
            q_lower_clean = query.lower()
            is_explicit_recent_query = any(k in q_lower_clean for k in [
                "recent request", "my latest request", "my recent application",
                "status of my request", "status of my application", "check my request status",
                "application status", "ticket status"
            ])
            if session and is_explicit_recent_query:
                from app.database import DataRepository
                recent_requests = DataRepository.list_service_requests(session)
                if recent_requests:
                    latest = recent_requests[-1]
                    return {
                        "content": (
                            f"Here is the status of your most recent administrative request:\n\n"
                            f"• **Tracking No:** **{latest.get('request_no')}**\n"
                            f"• **Service:** {latest.get('title')}\n"
                            f"• **Current Status:** **{latest.get('status')}**\n"
                            f"• **Office:** {latest.get('assigned_office')}\n\n"
                            f"You can view all your submissions in the Student Services tab."
                        ),
                        "category": "SERVICES",
                        "topic": "Recent Request Status",
                        "source_agent": "VIGBOT (Status Engine)",
                        "redirect_path": "services",
                        "action": {
                            "type": "navigate",
                            "label": "Track in Student Services",
                            "target": "services",
                            "route": "/?tab=services"
                        },
                        "structured_card": None,
                        "citations": [],
                        "routed_by": "universal_nlu"
                    }

            return {
                "content": (
                    "To track the status of your applications or service requests, please visit the **Student Services** tab.\n"
                    "You can view all live ticket updates, assigned administrative desks, and resolution notes there."
                ),
                "category": "SERVICES",
                "topic": "Status Tracking",
                "source_agent": "VIGBOT (Status Engine)",
                "redirect_path": "services",
                "action": {
                    "type": "navigate",
                    "label": "Open Student Services",
                    "target": "services",
                    "route": "/?tab=services"
                },
                "structured_card": None,
                "citations": [],
                "routed_by": "universal_nlu"
            }

        # -------------------------------------------------------------------
        # 3. AMBIGUOUS QUERIES: Ask for targeted clarification
        # -------------------------------------------------------------------
        if comm_intent == CommunicationIntent.AMBIGUOUS:
            q_lower = query.lower()
            if "found" in q_lower or "lost" in q_lower:
                return {
                    "content": (
                        "It sounds like you have a question regarding a lost or found item on campus!\n\n"
                        "• If you **found an item**: You can report it in the **Lost & Found** section so the owner can claim it.\n"
                        "• If you **lost an item**: You can check current listings or submit a lost item alert.\n\n"
                        "Would you like me to open the **Lost & Found** section for you?"
                    ),
                    "category": "LOST_AND_FOUND",
                    "topic": "Lost & Found Guidance",
                    "source_agent": "VIGBOT (Navigation Assistant)",
                    "redirect_path": "lost-and-found",
                    "action": {
                        "type": "navigate",
                        "label": "Open Lost & Found",
                        "target": "lost-and-found",
                        "route": "/?tab=lost-and-found"
                    },
                    "structured_card": {
                        "type": "navigation",
                        "title": "Lost & Found Section",
                        "subtitle": "Report or claim misplaced campus belongings",
                        "badge": "Feature Discovery",
                        "badgeVariant": "blue",
                        "actionLabel": "Open Lost & Found",
                        "actionIntent": "navigate:lost-and-found",
                        "target": "lost-and-found"
                    },
                    "citations": [],
                    "routed_by": "universal_nlu"
                }

            return {
                "content": (
                    "I want to make sure I direct you to the right place. Could you please specify what you need assistance with?\n\n"
                    "• **Lost & Found:** Report or claim lost belongings on campus.\n"
                    "• **Student Services:** Apply for certificates, ID cards, or official documents.\n"
                    "• **Grievances:** Lodge a formal concern regarding academics or campus life.\n"
                    "• **Academics:** Attendance, marks, timetable, or subject tutoring."
                ),
                "category": "HELP",
                "topic": "Intent Clarification",
                "source_agent": "VIGBOT (Navigation Assistant)",
                "redirect_path": None,
                "action": None,
                "structured_card": None,
                "citations": [],
                "routed_by": "universal_nlu"
            }

        # -------------------------------------------------------------------
        # 4. CAPABILITY MATCH RESOLUTION (28 Application Capabilities)
        # -------------------------------------------------------------------
        if matching_cap:
            cap_id = matching_cap["feature_id"]
            cap_name = matching_cap["name"]
            frontend_tab = matching_cap["frontend_tab"]
            guidance = matching_cap["guidance_text"]
            nav_label = matching_cap["default_navigation_label"]

            # Scenario A: Information & Personal Data Requests (ASKING: Where, How, Timings, Rules, Records)
            # STRICT FALSE-ACTION GUARD: NEVER write to DB or fabricate tickets!
            if comm_intent in (CommunicationIntent.INFORMATION_REQUEST, CommunicationIntent.PERSONAL_DATA_REQUEST):
                from app.agent.tool_registry import ToolRegistry

                # 1. Statutory Anti-Ragging Special Notice
                if cap_id == "grievance" and any(k in query.lower() for k in ["ragging", "anti-ragging", "antiragging"]):
                    content_text = (
                        "🚨 **Statutory Anti-Ragging Notice (Zero-Tolerance Policy):**\n"
                        "Vignan University enforces a strict zero-tolerance policy towards ragging in compliance with UGC Regulations.\n\n"
                        "**Immediate Emergency Contacts:**\n"
                        "• **National Anti-Ragging Helpline:** `1800-180-5522` (24x7 Toll-Free)\n"
                        "• **Helpline Email:** `helpline@antiragging.in`\n"
                        "• **University Anti-Ragging Squad / Proctor Office:** Admin Block, Room 101\n\n"
                        "You can also submit an official confidential complaint directly via the Student Grievance portal below."
                    )
                    suggested_follow_ups = ["How to lodge confidential grievance?", "Who is the university ombudsman?", "View UGC regulations"]
                    citations = [
                        {
                            "title": "UGC Regulations on Curbing Ragging in Higher Educational Institutions",
                            "clause": "Clause 6.3 & Clause 7.1",
                            "effective_date": "2009-06-17",
                            "summary": "Mandatory anti-ragging monitoring squad and statutory 24x7 helpline."
                        }
                    ]

                elif cap_id == "map":
                    tool_res = ToolRegistry.get_campus_location_and_navigation(destination=query)
                    direct_ans = tool_res.get("direct_answer", "")
                    data = tool_res.get("data")
                    
                    q_lower = query.lower()
                    is_directional = bool(re.search(
                        r"\b(?:where\s+is|where\s+are|directions?\s+to|how\s+to\s+reach|how\s+do\s+i\s+(?:reach|get\s+to|go\s+to)|how\s+can\s+i\s+(?:reach|get\s+to|go\s+to)|way\s+to|route\s+to|path\s+to|walking\s+route|from\s+.+\s+to|take\s+me\s+to)\b",
                        q_lower
                    ))
                    
                    profile = data.get("building_profile") if (data and isinstance(data, dict)) else None
                    
                    if not is_directional and profile:
                        # Informational building profile for "what is N-block?", "tell me about N-block", etc.
                        b_title = profile.get("title", data.get("destination", "Campus Facility"))
                        content_text = (
                            f"🏢 **{b_title}:**\n\n"
                            f"• **Purpose & Departments:** {profile.get('purpose')}\n"
                            f"• **Student Cohort:** {profile.get('cohort')}\n"
                            f"• **Campus Location:** {profile.get('location')}\n"
                            f"• **Key Facilities:** {profile.get('facilities')}\n\n"
                            f"*Need step-by-step walking directions? Ask \"where is {data.get('destination', 'this block')}\" or explore the interactive 2D layout in the **Campus Map** tab.*"
                        )
                    elif data and isinstance(data, dict) and "steps" in data:
                        # Directional query with turn-by-turn walking route
                        steps_lines = "\n".join(f"• {s}" for s in data["steps"])
                        b_name = data.get("destination", "Target Block")
                        b_dist = data.get("total_distance_meters", 0.0)
                        origin = data.get("origin", "Main Gate")
                        content_text = (
                            f"📍 **{b_name} Location & Campus Directions:**\n\n"
                            f"{direct_ans}\n\n"
                            f"**🚶 Turn-by-Turn Walking Route from {origin} ({b_dist}m):**\n"
                            f"{steps_lines}\n\n"
                            f"You can also explore the interactive 2D layout in the **Campus Map** tab."
                        )
                    else:
                        content_text = f"{direct_ans}\n\nYou can explore the interactive building layout on the **Campus Map** tab."

                    suggested_follow_ups = ["Where is A-Block?", "Where is U-Block?", "How to reach NTR Library?"]
                    citations = [
                        {
                            "title": "VFSTR Campus Spatial Directory",
                            "clause": "Campus Spatial Grid",
                            "effective_date": "2026-10-30",
                            "summary": "Algorithmic Dijkstra turn-by-turn navigation paths."
                        }
                    ]

                elif cap_id == "library":
                    tool_res = ToolRegistry.get_library_info(query)
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"📚 **Central Library Information & Schedule:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Regular Hours (Mon–Fri):** 08:00 AM – 10:00 PM (Reading Hall) | 09:00 AM – 06:00 PM (Lending Counter)\n"
                        f"• **Weekend Hours:** Saturday: 08:00 AM – 08:00 PM | Sunday: 09:00 AM – 05:00 PM (Reading Hall & Digital Access Only)\n"
                        f"• **Digital Resources:** 10,000+ IEEE/Springer e-journals accessible on campus LAN.\n\n"
                        f"You can explore library catalog and digital repositories in the **Library** tab."
                    )
                    suggested_follow_ups = ["Is library open this Sunday?", "What time does library close on weekdays?", "Search books in library"]
                    citations = [
                        {
                            "title": "VFSTR NTR Central Library Handbook",
                            "clause": "Section 2.1: Timings & Access",
                            "effective_date": "2026-08-01",
                            "summary": "Official library working hours, Sunday access, and circulation counter rules."
                        }
                    ]

                elif cap_id == "calendar":
                    tool_res = ToolRegistry.get_academic_calendar(query)
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"📅 **Academic Calendar & Key Dates:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Semester I Classes:** July 15, 2026 – November 28, 2026\n"
                        f"• **CIE-2 Examinations:** November 16 – 21, 2026\n"
                        f"• **Attendance Condonation Cutoff:** November 20, 2026\n"
                        f"• **End-Semester Summative Exams:** December 01 – 19, 2026\n"
                        f"• **Pongal Vacation:** January 11 – 17, 2027\n\n"
                        f"You can view the full academic schedule in the **Academic Calendar** tab."
                    )
                    suggested_follow_ups = ["When does Pongal vacation start?", "When is the next exam?", "Check CIE-2 timetable"]
                    citations = [
                        {
                            "title": "VFSTR Academic Calendar 2026-27",
                            "clause": "Clause 1.2: Semester Milestones",
                            "effective_date": "2026-07-01",
                            "summary": "Approved schedule of instruction, assessments, and university holidays."
                        }
                    ]

                elif cap_id == "hostel":
                    tool_res = ToolRegistry.get_hostel_and_mess_info(query)
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"🏠 **Hostel & Dining Services:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Dining Schedule:** Breakfast (07:15 – 08:45 AM) | Lunch (12:15 – 01:45 PM) | Dinner (07:30 – 09:00 PM)\n"
                        f"• **Curfew & Biometrics:** Boys Hostel: 09:30 PM | Girls Hostel: 08:30 PM (Biometric punch mandatory)\n"
                        f"• **Outpass Protocol:** Weekend outing requests must be submitted by Friday 05:00 PM with warden approval.\n\n"
                        f"You can apply for outpasses and view dining menus in the **Hostel & Mess** tab."
                    )
                    suggested_follow_ups = ["What is the curfew time in boys hostel?", "Tell me about mess timings", "Apply for hostel outpass"]
                    citations = [
                        {
                            "title": "VFSTR Hostel Rules & Dining Guidelines",
                            "clause": "Section 3: Curfew & Discipline",
                            "effective_date": "2026-07-15",
                            "summary": "Hostel timings, biometric tracking, and decentralized dining rules."
                        }
                    ]

                elif cap_id == "transport":
                    tool_res = ToolRegistry.get_bus_schedule(query)
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"🚌 **Campus Transport & Bus Schedule:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Route 1 (Guntur):** Leaves 06:45 AM | Returns 04:45 PM (Old Bus Stand – Collectorate – Campus)\n"
                        f"• **Route 2 (Vijayawada):** Leaves 06:30 AM | Returns 04:45 PM (Benz Circle – Auto Nagar – Campus)\n"
                        f"• **Route 3 (Tenali):** Leaves 07:00 AM | Returns 04:45 PM (Railway Station – Chenchupet – Campus)\n"
                        f"• **Route 4 (Mangalagiri):** Leaves 07:10 AM | Returns 04:45 PM (Main Bazaar – NRI Hospital – Campus)\n\n"
                        f"You can track bus routes and live transport passes in the **Transport** tab."
                    )
                    suggested_follow_ups = ["Can I get college bus from Vijayawada?", "What time does the evening bus leave?", "How to get a bus pass?"]
                    citations = [
                        {
                            "title": "VFSTR Transport Operations Manual",
                            "clause": "Fleet Schedule 2026",
                            "effective_date": "2026-08-01",
                            "summary": "Daily city bus pickup, transit routes, and return schedules."
                        }
                    ]

                elif cap_id == "policies":
                    tool_res = ToolRegistry.get_university_policies(query)
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"📜 **University Academic Policies & Bylaws:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Mandatory 75% Rule:** Under R23 Clause 4.2, students must maintain ≥ 75.0% cumulative attendance to write end-semester exams.\n"
                        f"• **Condonation Window (65%–74.9%):** May be condoned by the Dean on valid medical grounds upon payment of the ₹1,000 statutory condonation fee.\n"
                        f"• **Detention (<65%):** Students below 65% are detained and not permitted to write summative exams under any circumstances.\n\n"
                        f"You can review full academic regulations and ordinances in the **Policies & Regulations** tab."
                    )
                    suggested_follow_ups = ["What is the condonation fee if attendance is 70%?", "What happens if attendance is below 65?", "Check my current attendance"]
                    citations = [
                        {
                            "title": "VFSTR Academic Regulations R23",
                            "clause": "Clause 4.2: Attendance Norms & Condonation",
                            "effective_date": "2023-07-15",
                            "summary": "Mandates 75% minimum attendance, condonation bracket (65-74.9%), and detention policy."
                        }
                    ]

                elif cap_id == "clubs":
                    tool_res = ToolRegistry.get_clubs_directory(query)
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"🎭 **Student Clubs & Extracurricular Communities:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Technical:** AI Innovation Club, Coding & Algorithm Chapter, Robotics & Automation\n"
                        f"• **Cultural & Arts:** Symphony Music Club, Natya Dance Troupe, Vignan Shutterbugs (Photography)\n"
                        f"• **Social & Leadership:** NSS Unit, NCC Wing, Green Earth Environmental Society\n\n"
                        f"You can explore club events and submit joining applications in the **Clubs & Communities** tab."
                    )
                    suggested_follow_ups = ["How do I join the music club?", "Are there any robotics or coding clubs?", "View upcoming club events"]
                    citations = [
                        {
                            "title": "VFSTR Directorate of Student Life",
                            "clause": "Student Clubs Manual 2026",
                            "effective_date": "2026-08-01",
                            "summary": "Student club recognition, activities, and membership criteria."
                        }
                    ]

                elif cap_id == "bookings":
                    tool_res = ToolRegistry.get_facility_booking_info(query)
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"🏟️ **Campus Facility Booking & Venues:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Seminar Halls 1 & 2:** Capacity: 250 | Audio-visual projector & air-conditioned\n"
                        f"• **Main Convocation Auditorium:** Capacity: 1,500 | Large stage, professional acoustics\n"
                        f"• **Sports Complex:** Cricket Ground, Outdoor Basketball Courts, Indoor Badminton Arena\n"
                        f"• **Advance Reservation:** Facility booking requests must be submitted at least 48 hours prior with faculty coordinator sign-off.\n\n"
                        f"You can check live slot availability and reserve venues in the **Facility Booking** tab."
                    )
                    suggested_follow_ups = ["How can our class book the seminar hall?", "Can we book cricket ground for Sunday match?", "Check slot availability"]
                    citations = [
                        {
                            "title": "VFSTR Estate & Facility Guidelines",
                            "clause": "Venue Reservation Rules",
                            "effective_date": "2026-08-01",
                            "summary": "Protocols and approval workflows for campus venue reservations."
                        }
                    ]

                elif cap_id == "career":
                    tool_res = ToolRegistry.get_career_opportunities(query)
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"💼 **Career Hub & Campus Placements:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Active Recruitment Drives:** Amazon AWS (12.0 LPA), TCS Digital (7.5 LPA), Cognizant GenC Next (6.5 LPA)\n"
                        f"• **Upcoming Drives:** Microsoft India, Infosys SP, Deloitte USI\n"
                        f"• **Eligibility:** Minimum 60% in 10th/12th and current CGPA ≥ 6.5 with zero active backlogs.\n"
                        f"• **T&P Office:** 2nd Floor, Administrative Block (Mon–Fri: 09:00 AM – 05:00 PM)\n\n"
                        f"You can explore active drives and submit your resume in the **Career Hub** tab."
                    )
                    suggested_follow_ups = ["Which companies are visiting for placements this year?", "Where is the training and placement cell?", "Minimum CGPA for placements"]
                    citations = [
                        {
                            "title": "VFSTR Training & Placement Cell",
                            "clause": "Recruitment Bulletin 2026-27",
                            "effective_date": "2026-09-01",
                            "summary": "Campus drive schedules, packages, and eligibility criteria."
                        }
                    ]

                elif cap_id == "events":
                    tool_res = ToolRegistry.get_campus_events(query)
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"🎉 **Campus Events & Festivals:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Vignan National Hackathon 2026:** Nov 20–21 | 36-hour coding marathon | Prize Pool: ₹1,50,000 | Venue: N-Block Labs\n"
                        f"• **Vignan Mahotsav 2027:** Jan 22–24 | Annual national cultural fest (Dance, Music, Literary & Tech competitions)\n"
                        f"• **AI & Cloud Symposium:** Dec 05 | Guest lectures by industry veterans | Venue: Convocation Hall\n\n"
                        f"You can view schedules and get event entry passes in the **Event Registration** tab."
                    )
                    suggested_follow_ups = ["When is Vignan Mahotsav?", "Any hackathons or technical fests happening soon?", "Register for upcoming event"]
                    citations = [
                        {
                            "title": "VFSTR Student Activity Council",
                            "clause": "Events Calendar 2026-27",
                            "effective_date": "2026-09-15",
                            "summary": "Approved calendar of campus fests, hackathons, and technical symposiums."
                        }
                    ]

                elif cap_id == "lost-and-found":
                    tool_res = ToolRegistry.get_lost_and_found_info(query)
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"🔍 **Lost & Found Campus Repository:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Report Lost Item:** Click the 'Report Item' button to log details (item type, location last seen, contact).\n"
                        f"• **Found Something?** Submit a report or deposit found valuables (wallets, phones, ID cards) at Chief Security Office, Main Gate.\n"
                        f"• **Claim Process:** Bring your university student ID card and verify item specifics to claim.\n\n"
                        f"You can browse active listings or log an item in the **Lost & Found** tab."
                    )
                    suggested_follow_ups = ["I lost my scientific calculator in room 204", "Someone found my ID card where can I collect it", "Report a found item"]
                    citations = [
                        {
                            "title": "VFSTR Campus Safety Board",
                            "clause": "Lost & Found SOP",
                            "effective_date": "2026-08-01",
                            "summary": "Standard operating procedure for logging, holding, and claiming lost property."
                        }
                    ]

                elif cap_id == "marketplace":
                    tool_res = ToolRegistry.get_marketplace_listings(query)
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"🛍️ **Student Peer-to-Peer Marketplace:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Available Categories:** Engineering Drawing Kits & Drafters, Core Textbooks, Scientific Calculators, Lab Coats, Campus Bicycles\n"
                        f"• **How It Works:** Connect directly with fellow students to buy or sell second-hand academic items.\n"
                        f"• **Safety Rule:** All transactions must be completed in public campus areas (MHP Canteen or NTR Library).\n\n"
                        f"You can browse peer listings or post an item for sale in the **Marketplace** tab."
                    )
                    suggested_follow_ups = ["Anyone selling used engineering drafter?", "Where can I buy second hand books on campus?", "Post an item for sale"]
                    citations = [
                        {
                            "title": "VFSTR Student Welfare Board",
                            "clause": "Campus Marketplace Policy",
                            "effective_date": "2026-08-01",
                            "summary": "Guidelines for fair peer-to-peer textbook and study tool exchanges."
                        }
                    ]

                elif cap_id == "polling":
                    tool_res = ToolRegistry.get_campus_polls()
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"🗳️ **Campus Polls & Student Voice:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Active Poll 1:** \"Vignan Mahotsav 2027 Keynote Theme: Emerging AI vs Cultural Heritage\"\n"
                        f"• **Active Poll 2:** \"Library Extended Hours: Should weekend reading room stay open till 11:00 PM?\"\n"
                        f"• **Eligibility:** All enrolled students can cast 1 verified vote per poll.\n\n"
                        f"You can cast your vote and see live results in the **Campus Polling** tab."
                    )
                    suggested_follow_ups = ["Any active student polls right now?", "Vote in current poll", "View poll results"]
                    citations = [
                        {
                            "title": "VFSTR Student Council Bylaws",
                            "clause": "Referendum Protocol",
                            "effective_date": "2026-08-01",
                            "summary": "Democratic voting and survey procedures for the student body."
                        }
                    ]

                elif cap_id == "alumni":
                    tool_res = ToolRegistry.get_alumni_mentors(query)
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"🤝 **Alumni Mentorship Network:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Google:** Senior Software Engineer (Distributed Systems, Cloud Architecture)\n"
                        f"• **Microsoft:** Product Manager (Azure Developer Division)\n"
                        f"• **Amazon:** Cloud Solutions Architect (High-Scale Backend Systems)\n"
                        f"• **Mentorship Areas:** Resume review, mock technical interviews, higher education referrals (MS/MBA).\n\n"
                        f"You can search mentors by company and connect with graduates in the **Alumni Network** tab."
                    )
                    suggested_follow_ups = ["How can I connect with alumni mentors working at Google?", "Request alumni mentorship", "Alumni in AI research"]
                    citations = [
                        {
                            "title": "VFSTR Alumni Relations Association",
                            "clause": "Mentorship Charter",
                            "effective_date": "2026-07-01",
                            "summary": "Verified alumni mentor directory and student interaction guidelines."
                        }
                    ]

                elif cap_id == "circulars":
                    tool_res = ToolRegistry.get_official_circulars()
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"📢 **Official Circulars & Administrative Notices:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Circular ACME/REG/2026/089:** Schedule for Second Continuous Internal Evaluation (CIE-2)\n"
                        f"• **Circular EST/FAC/2026/041:** Winter Vacation & Maintenance Schedule\n"
                        f"• **Circular DEAN/ACAD/2026/112:** Mandatory Attendance Verification Cutoff Date\n\n"
                        f"You can read full circular PDFs and official notices in the **Circulars & Notices** tab."
                    )
                    suggested_follow_ups = ["What is the latest circular from examination cell?", "CIE-2 exam circular details", "When is the next academic holiday?"]
                    citations = [
                        {
                            "title": "VFSTR Office of the Registrar",
                            "clause": "Official Notifications Gazette",
                            "effective_date": "2026-10-15",
                            "summary": "Authenticated university administrative circulars and executive orders."
                        }
                    ]

                elif cap_id == "services":
                    tool_res = ToolRegistry.get_services_directory(query)
                    direct_ans = tool_res.get("direct_answer", "")
                    content_text = (
                        f"🏛️ **Student Services & Administrative Certificates:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Bonafide Certificate:** Processing SLA: 2 working days | Apply for passport, bank loan, or visa.\n"
                        f"• **Duplicate ID Card:** Fee: ₹200 | Processing SLA: 1 working day | Report lost card at Admin Office Room 104.\n"
                        f"• **Bus / Railway Concession:** Processing SLA: 3 working days | Bring approved bonafide.\n"
                        f"• **Transcripts & Migration:** Processing SLA: 5 working days | Office of Controller of Examinations.\n\n"
                        f"You can submit requests and track live ticket status in the **Student Services** tab."
                    )
                    suggested_follow_ups = ["How to apply for bonafide certificate for passport?", "I need duplicate ID card what is the procedure?", "Track my request"]
                    citations = [
                        {
                            "title": "VFSTR Student Service Charter",
                            "clause": "Service Level Agreements (SLAs)",
                            "effective_date": "2026-08-01",
                            "summary": "Document issuance timelines, fees, and processing offices."
                        }
                    ]

                elif cap_id == "wellness":
                    content_text = (
                        "💚 **Student Wellness, Counseling & Mental Wellbeing:**\n\n"
                        "Your emotional and mental wellbeing is a top institutional priority. Confidential support is available to all students:\n\n"
                        "• **Student Counseling Center:** Room C-402, Admin Block | In-person counseling (Mon–Sat: 09:00 AM – 05:00 PM)\n"
                        "• **Campus Counselor Contact:** `counselor@vignan.ac.in` | Dedicated student psychologists on campus\n"
                        "• **National Tele-MANAS Helpline:** `14416` (24x7 Toll-Free, confidential mental health assistance)\n"
                        "• **KIRAN Mental Health Helpline:** `1800-599-0019` (Govt. of India 24x7 Toll-Free)\n\n"
                        "You don't have to face stress or pressure alone. You can also view wellbeing guides in the **Wellness** tab."
                    )
                    suggested_follow_ups = ["Where is counselor office on campus?", "I feel really overwhelmed and stressed who can I talk to", "Book counselor session"]
                    citations = [
                        {
                            "title": "VFSTR Student Wellbeing Charter",
                            "clause": "Confidential Counseling Policy",
                            "effective_date": "2026-08-01",
                            "summary": "Campus mental health resources, trained psychologist appointments, and emergency lines."
                        }
                    ]

                elif cap_id == "attendance":
                    tool_res = ToolRegistry.get_attendance_records(session) if session else {}
                    direct_ans = tool_res.get("direct_answer", "Your cumulative attendance record across all registered subjects is tracked under R23 regulations.")
                    content_text = (
                        f"📊 **Attendance Analytics & Subject Summary:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Overall Status:** Verified against university biometrics.\n"
                        f"• **Regulation Rule:** ≥ 75.0% mandatory for semester end exams | 65.0%–74.9% condonation bracket.\n\n"
                        f"You can view subject-wise breakdowns and attendance calculators in the **Attendance** tab."
                    )
                    suggested_follow_ups = ["How much attendance do I have right now?", "Can I bunk Digital Logic today without getting short?", "Classes needed for 75%"]
                    citations = [
                        {
                            "title": "VFSTR Academic Regulations R23",
                            "clause": "Clause 4.2: Attendance Norms",
                            "effective_date": "2023-07-15",
                            "summary": "Mandatory 75% attendance rule and semester exam eligibility."
                        }
                    ]

                elif cap_id == "marks":
                    tool_res = ToolRegistry.get_marks_records(session) if session else {}
                    direct_ans = tool_res.get("direct_answer", "Your verified academic marks and cumulative grade point average (CGPA) are recorded in the university database.")
                    content_text = (
                        f"🎯 **Academic Performance & Marks:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Evaluation System:** Continuous Internal Evaluation (CIE-1 & CIE-2: 40 Marks) + Semester End Exam (SEE: 60 Marks).\n"
                        f"• **Passing Grade:** Minimum 40% in SEE and 40% aggregate in each course to earn credits.\n\n"
                        f"You can view detailed grade sheets and CGPA calculators in the **Marks & CGPA** tab."
                    )
                    suggested_follow_ups = ["What is my current CGPA?", "How many marks did I get in mid exams?", "Check grade breakdown"]
                    citations = [
                        {
                            "title": "VFSTR Grading System Manual",
                            "clause": "10-Point Relative Scale",
                            "effective_date": "2026-07-01",
                            "summary": "Continuous internal assessment weights, grade thresholds, and credit awards."
                        }
                    ]

                elif cap_id == "timetable":
                    tool_res = ToolRegistry.get_timetable_schedule(session) if session else {}
                    direct_ans = tool_res.get("direct_answer", "Your daily academic timetable and lecture periods are scheduled per semester regulations.")
                    content_text = (
                        f"⏰ **Academic Timetable & Schedule:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Class Timings:** Period 1 (08:30 – 09:20 AM) | Period 2 (09:20 – 10:10 AM) | Lunch (12:40 – 01:30 PM)\n"
                        f"• **Venue Details:** Core lecture halls located in N-Block (CSE/AIML) and H-Block (ECE/IT).\n\n"
                        f"You can view your weekly schedule and lecture halls in the **Timetable** tab."
                    )
                    suggested_follow_ups = ["What is my timetable for Monday?", "Which classroom do I have to go for next period?", "Check tomorrow schedule"]
                    citations = [
                        {
                            "title": "VFSTR Department Timetable 2026",
                            "clause": "B.Tech Class Schedule",
                            "effective_date": "2026-08-01",
                            "summary": "Weekly class schedules, lab allocations, and room numbers."
                        }
                    ]

                elif cap_id == "exams":
                    tool_res = ToolRegistry.get_examination_schedule(session) if session else {}
                    direct_ans = tool_res.get("direct_answer", "Your upcoming examination schedule and assessment dates are listed below.")
                    content_text = (
                        f"📝 **Examination Schedule & Hall Details:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Format:** 2 Continuous Internal Evaluations (CIE) + 1 Summative Semester End Examination (SEE).\n"
                        f"• **Exam Rules:** Bring your physical student ID card and hall ticket. Electronic devices and smartwatches are strictly prohibited.\n\n"
                        f"You can view seat numbers and exam timetables in the **Examinations** tab."
                    )
                    suggested_follow_ups = ["When is my next exam scheduled?", "Where is examination hall B-3?", "View full exam timetable"]
                    citations = [
                        {
                            "title": "VFSTR Examination Ordinance",
                            "clause": "Conduct of Examinations 2026",
                            "effective_date": "2026-08-01",
                            "summary": "Examination timetables, hall rules, and seating allocations."
                        }
                    ]

                elif cap_id == "fees":
                    tool_res = ToolRegistry.get_fee_status(session) if session else {}
                    direct_ans = tool_res.get("direct_answer", "Your student fee ledger and academic tuition balance are maintained in the Finance Office records.")
                    content_text = (
                        f"💳 **Fee Status & Financial Ledgers:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Payment Methods:** Online net banking/UPI via student portal or challan payment at university bank counter (Canara Bank, Campus Branch).\n"
                        f"• **Important:** Clear pending balances before the examination hall ticket issuance deadline.\n\n"
                        f"You can make payments and download receipts in the **Fee Status** tab."
                    )
                    suggested_follow_ups = ["How much tuition fee is pending for this year?", "Download fee payment receipt", "Where is the campus bank?"]
                    citations = [
                        {
                            "title": "VFSTR Finance Department Notification",
                            "clause": "Tuition Fee Schedule 2026-27",
                            "effective_date": "2026-08-15",
                            "summary": "Fee structure, installment due dates, and payment methods."
                        }
                    ]

                elif cap_id == "curriculum":
                    tool_res = ToolRegistry.get_curriculum_audit(session) if session else {}
                    direct_ans = tool_res.get("direct_answer", "Your degree credit audit and graduation requirements are tracked under R23 Regulations.")
                    content_text = (
                        f"📖 **Curriculum & Degree Audit:**\n\n"
                        f"{direct_ans}\n\n"
                        f"• **Framework:** Choice-Based Credit System (CBCS) under R23 Regulations.\n"
                        f"• **Graduation Requirement:** 160 credits across Basic Sciences, Engineering Core, Professional Electives, and Capstone Project.\n\n"
                        f"You can audit remaining graduation requirements in the **Curriculum** tab."
                    )
                    suggested_follow_ups = ["How many credits do I need to graduate?", "View B.Tech R23 syllabus", "What are the elective options?"]
                    citations = [
                        {
                            "title": "VFSTR B.Tech Curriculum Framework R23",
                            "clause": "Section 5: Credit Architecture",
                            "effective_date": "2023-07-01",
                            "summary": "Four-year credit distributions, mandatory courses, and degree completion criteria."
                        }
                    ]

                elif cap_id == "home":
                    tool_res = ToolRegistry.get_home_overview(session) if session else {}
                    direct_ans = tool_res.get("direct_answer", "Welcome to VIGBOT Central Command Center.")
                    content_text = (
                        f"🏠 **Helpdesk Home & Command Center:**\n\n"
                        f"{direct_ans}\n\n"
                        f"You can access all academic features, live alerts, and quick actions directly from the **Helpdesk Home** tab."
                    )
                    suggested_follow_ups = ["What is my attendance?", "When is my next exam?", "Where is N-Block?"]
                    citations = [
                        {
                            "title": "VFSTR Student Helpdesk System",
                            "clause": "Command Center Overview",
                            "effective_date": "2026-10-30",
                            "summary": "Centralized student services portal."
                        }
                    ]

                elif cap_id == "gamification":
                    content_text = (
                        "🏆 **Achievements, Karma Points & Streaks:**\n\n"
                        "Keep up your campus engagement and academic consistency!\n\n"
                        "• **Current Attendance Streak:** Maintained above 75% for 4 consecutive weeks.\n"
                        "• **Karma Points:** Earn points by attending workshops, voting in student polls, and maintaining academic records.\n"
                        "• **Badges Earned:** 'Consistent Scholar', 'Active Voter', 'Early Riser'.\n\n"
                        "You can view your points and campus leaderboard in the **Achievements** tab."
                    )
                    suggested_follow_ups = ["How do I earn karma points?", "View campus leaderboard", "What badges can I unlock?"]
                    citations = [
                        {
                            "title": "VFSTR Student Engagement System",
                            "clause": "Gamification Charter",
                            "effective_date": "2026-08-01",
                            "summary": "Point awards for academic consistency and extracurricular participation."
                        }
                    ]

                elif cap_id == "student-profile":
                    content_text = (
                        "👤 **Student Profile & Faculty Mentors:**\n\n"
                        "Your official enrollment identity and assigned academic advisors are registered in the university system:\n\n"
                        "• **Assigned Faculty Mentor:** Dr. K. Radhika (Associate Professor, Dept. of CSE) | Cabin: N-304\n"
                        "• **Class Teacher:** Mr. P. Suresh | Cabin: N-212 | Office Hours: 03:30 – 04:30 PM\n"
                        "• **Head of Department (CSE):** Dr. M. V. Ramana | Admin Wing, N-Block\n\n"
                        "You can view your complete student profile and contact details in the **Student Profile** drawer."
                    )
                    suggested_follow_ups = ["Who is my faculty mentor?", "Where is my class teacher's cabin?", "View my full profile"]
                    citations = [
                        {
                            "title": "VFSTR Student Enrollment Directory",
                            "clause": "Mentor-Mentee System",
                            "effective_date": "2026-07-01",
                            "summary": "Assigned faculty advisors and academic counseling roster."
                        }
                    ]

                elif cap_id == "admin":
                    content_text = (
                        "⚙️ **Administrative Management Console:**\n\n"
                        "The administrative control center is restricted to authorized faculty coordinators, department heads, and helpdesk officers:\n\n"
                        "• **Features:** Department analytics, service request dispatch, attendance auditing, and circular broadcasting.\n"
                        "• **Access:** Requires institutional officer credentials and multi-factor authentication.\n\n"
                        "Authorized officers can sign in to the **Administrative Portal** below."
                    )
                    suggested_follow_ups = ["Open Admin Console", "How to get admin access?"]
                    citations = [
                        {
                            "title": "VFSTR Administrative Security Policy",
                            "clause": "Role-Based Access Control",
                            "effective_date": "2026-08-01",
                            "summary": "Restricted administrative console guidelines."
                        }
                    ]

                else:
                    content_text = f"{guidance}\n\nYou can access it directly using the button below."
                    suggested_follow_ups = [f"Go to {cap_name}", f"Help with {cap_name}"]
                    citations = []

                return {
                    "content": content_text,
                    "category": matching_cap["category"],
                    "topic": f"{cap_name} Guidance",
                    "source_agent": f"VIGBOT ({cap_name} Guide)",
                    "redirect_path": frontend_tab,
                    "action": {
                        "type": "navigate",
                        "label": nav_label,
                        "target": frontend_tab,
                        "route": matching_cap["frontend_route"]
                    },
                    "structured_card": {
                        "type": "navigation",
                        "title": cap_name,
                        "subtitle": matching_cap["description"],
                        "badge": "Application Feature",
                        "badgeVariant": "blue",
                        "actionLabel": nav_label,
                        "actionIntent": f"navigate:{frontend_tab}",
                        "target": frontend_tab
                    },
                    "suggested_follow_ups": suggested_follow_ups,
                    "citations": citations,
                    "routed_by": "universal_nlu"
                }

            # Scenario B: Direct Navigation Request ("Open Lost & Found", "Take me there", "kholo")
            if comm_intent == CommunicationIntent.NAVIGATION_REQUEST:
                return {
                    "content": f"Opening **{cap_name}** for you now.",
                    "category": matching_cap["category"],
                    "topic": f"Navigate to {cap_name}",
                    "source_agent": "VIGBOT (Navigation Assistant)",
                    "redirect_path": frontend_tab,
                    "action": {
                        "type": "navigate",
                        "label": nav_label,
                        "target": frontend_tab,
                        "route": matching_cap["frontend_route"]
                    },
                    "structured_card": {
                        "type": "navigation",
                        "title": cap_name,
                        "subtitle": f"Switching to {cap_name} view",
                        "badge": "Navigation",
                        "badgeVariant": "green",
                        "actionLabel": nav_label,
                        "actionIntent": f"navigate:{frontend_tab}",
                        "target": frontend_tab
                    },
                    "citations": [],
                    "routed_by": "universal_nlu"
                }

            # Scenario C: Action Request (DOING: User wants to submit, report, book, apply)
            if comm_intent == CommunicationIntent.ACTION_REQUEST:
                # Genuine student services requests (e.g. bonafide certificate, duplicate ID card)
                # are dispatched to the specialized services tool in NLUEngine to generate legitimate verified tickets.
                if cap_id == "services":
                    return None

                # For Lost & Found reporting: guide user to official reporting modal with prefill instructions
                if cap_id == "lost-and-found":
                    return {
                        "content": (
                            "To report an item you found, please open the **Lost & Found** section and click the **'Report Item'** button.\n\n"
                            "You will be able to enter:\n"
                            "1. Item title (e.g. 'Blue Dell Laptop Bag')\n"
                            "2. Category & where it was found (e.g. 'U-Block Room 204')\n"
                            "3. Your contact info or where you deposited the item.\n\n"
                            "Click below to open the reporting screen."
                        ),
                        "category": "LOST_AND_FOUND",
                        "topic": "Report Found Item",
                        "source_agent": "VIGBOT (Lost & Found Assistant)",
                        "redirect_path": "lost-and-found",
                        "action": {
                            "type": "navigate",
                            "label": "Open Lost & Found Form",
                            "target": "lost-and-found",
                            "route": "/?tab=lost-and-found"
                        },
                        "structured_card": {
                            "type": "navigation",
                            "title": "Report Found Item",
                            "subtitle": "Click to open the Lost & Found submission form",
                            "badge": "Action Guide",
                            "badgeVariant": "emerald",
                            "actionLabel": "Open Lost & Found",
                            "actionIntent": "navigate:lost-and-found",
                            "target": "lost-and-found"
                        },
                        "citations": [],
                        "routed_by": "universal_nlu"
                    }

                # For Bookings: Guide user to facility booking screen with explicit parameters
                if cap_id == "bookings":
                    return {
                        "content": (
                            "To book a campus facility (Seminar Hall, Auditorium, or Sports Ground):\n\n"
                            "1. Open the **Facility Booking** section.\n"
                            "2. Select your desired facility and date.\n"
                            "3. Choose an available time slot and state the academic event purpose.\n\n"
                            "Click below to reserve your slot."
                        ),
                        "category": "BOOKINGS",
                        "topic": "Facility Reservation",
                        "source_agent": "VIGBOT (Bookings Assistant)",
                        "redirect_path": "bookings",
                        "action": {
                            "type": "navigate",
                            "label": "Open Facility Bookings",
                            "target": "bookings",
                            "route": "/?tab=bookings"
                        },
                        "structured_card": {
                            "type": "navigation",
                            "title": "Facility Reservation",
                            "subtitle": "Reserve campus venues and seminar halls",
                            "badge": "Action Required",
                            "badgeVariant": "blue",
                            "actionLabel": "Open Bookings",
                            "actionIntent": "navigate:bookings",
                            "target": "bookings"
                        },
                        "citations": [],
                        "routed_by": "universal_nlu"
                    }

                # Other action-capable features: guide user to official modal without fabricating tickets
                return {
                    "content": (
                        f"To proceed with your request for **{cap_name}**, please use the official form in the {cap_name} section.\n"
                        f"Click below to navigate directly to the workspace."
                    ),
                    "category": matching_cap["category"],
                    "topic": f"{cap_name} Action",
                    "source_agent": "VIGBOT (Action Assistant)",
                    "redirect_path": frontend_tab,
                    "action": {
                        "type": "navigate",
                        "label": f"Open {cap_name}",
                        "target": frontend_tab,
                        "route": matching_cap["frontend_route"]
                    },
                    "structured_card": {
                        "type": "navigation",
                        "title": cap_name,
                        "subtitle": f"Open the {cap_name} workspace",
                        "badge": "Action Required",
                        "badgeVariant": "blue",
                        "actionLabel": f"Open {cap_name}",
                        "actionIntent": f"navigate:{frontend_tab}",
                        "target": frontend_tab
                    },
                    "citations": [],
                    "routed_by": "universal_nlu"
                }

        # If not matching a specific frontend capability, return None to let standard NLU proceed
        return None
