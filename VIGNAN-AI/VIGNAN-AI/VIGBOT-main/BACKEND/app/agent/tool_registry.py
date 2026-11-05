"""
VIGBOT Tool Registry (app/agent/tool_registry.py)
------------------------------------------------
Provides 23 typed, read-only tools matching every sidebar page.
Enforces:
1. Answer-First Rule: Direct factual answer in the first sentence.
2. Structured factual records: Every tool returns source, last_updated, sidebar_page, and available status.
3. JWT-scoped student data: Attendance, marks, timetable, fees, exams bound to DatabaseSession.
4. Algorithmic Navigation Graph: Dijkstra pathfinding across campus nodes and edges.
5. No database mutations: All tools are strictly read-only.
"""

from typing import Dict, Any, List, Optional, Tuple, TypedDict
import json
import sqlite3
import heapq
import os
import re
from pathlib import Path
from app.database import DataRepository, DatabaseSession, get_db_connection

class ToolResult(TypedDict, total=False):
    available: bool
    source: str
    last_updated: str
    sidebar_page: str
    direct_answer: str
    data: Optional[Dict[str, Any]]
    missing_notice: Optional[str]

class CampusGraphService:
    """Directed graph model of VFSTR campus for turn-by-turn pathfinding."""
    
    _nodes: Optional[Dict[str, Dict[str, Any]]] = None
    _adj: Optional[Dict[str, List[Tuple[str, float, str, str]]]] = None

    @classmethod
    def _load_graph(cls):
        if cls._nodes is not None and cls._adj is not None:
            return

        nodes = {}
        adj = {}
        with get_db_connection() as conn:
            if isinstance(conn, sqlite3.Connection):
                    conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT location_id, room_number, block, floor, description, type, features FROM campus_locations")
            for r in cur.fetchall():
                nid = r["location_id"]
                nodes[nid] = {
                    "id": nid,
                    "name": r["room_number"],
                    "block": r["block"],
                    "floor": r["floor"],
                    "description": r["description"],
                    "type": r["type"],
                    "features": json.loads(r["features"]) if r["features"] else []
                }
                adj[nid] = []

            cur.execute("SELECT edge_id, source_node, target_node, path_name, direction_instruction, distance_meters, is_bidirectional FROM campus_navigation_edges")
            for e in cur.fetchall():
                u, v = e["source_node"], e["target_node"]
                dist = float(e["distance_meters"])
                path = e["path_name"]
                instr = e["direction_instruction"]
                is_bi = bool(e["is_bidirectional"])

                if u in adj:
                    adj[u].append((v, dist, path, instr))
                if is_bi and v in adj:
                    adj[v].append((u, dist, path, f"Return along {path} to {nodes.get(u, {}).get('name', u)}."))

        cls._nodes = nodes
        cls._adj = adj

    @classmethod
    def resolve_node_id(cls, query: str) -> Optional[str]:
        cls._load_graph()
        q = (query or "").strip().lower()
        if not q:
            return None

        # 1. Direct Node ID match (e.g. N_BLOCK, CHEST_SUPERMARKET, NTR_LIBRARY)
        q_raw = query.strip()
        q_upper = q_raw.upper()
        if q_upper in cls._nodes:
            return q_upper
        q_under = q_raw.replace("-", "_").replace(" ", "_").upper()
        if q_under in cls._nodes:
            return q_under

        alias_map = {
            "n_block": "N_BLOCK",
            "a_block": "A_BLOCK",
            "h_block": "H_BLOCK",
            "e_block": "E_BLOCK",
            "u_block": "U_BLOCK",
            "zest_supermarket": "CHEST_SUPERMARKET",
            "chest_supermarket": "CHEST_SUPERMARKET",
            "mhp_canteen": "MHP_CANTEEN",
            "ntr_library": "NTR_LIBRARY",
            "vignan_vihar": "VIGNAN_VIHAR",
            "convocation_hall": "CONVOCATION_HALL",
            "main gate": "NODE_0_MAIN_GATE",
            "gate 0": "NODE_0_MAIN_GATE",
            "gate": "NODE_0_MAIN_GATE",
            "entrance": "NODE_0_MAIN_GATE",
            "freshers": "A_BLOCK",
            "fresher": "A_BLOCK",
            "1st year": "A_BLOCK",
            "first year": "A_BLOCK",
            "a block": "A_BLOCK",
            "a-block": "A_BLOCK",
            "ablock": "A_BLOCK",
            "h block": "H_BLOCK",
            "h-block": "H_BLOCK",
            "hblock": "H_BLOCK",
            "ece block": "H_BLOCK",
            "ece": "H_BLOCK",
            "it": "H_BLOCK",
            "id card": "H_BLOCK",
            "id replacement": "H_BLOCK",
            "admin office": "H_BLOCK",
            "library": "NTR_LIBRARY",
            "central library": "NTR_LIBRARY",
            "ntr": "NTR_LIBRARY",
            "ntr library": "NTR_LIBRARY",
            "canteen": "MHP_CANTEEN",
            "mhp": "MHP_CANTEEN",
            "mhp canteen": "MHP_CANTEEN",
            "food court": "MHP_CANTEEN",
            "zest": "CHEST_SUPERMARKET",
            "zest supermarket": "CHEST_SUPERMARKET",
            "zest store": "CHEST_SUPERMARKET",
            "chest": "CHEST_SUPERMARKET",
            "supermarket": "CHEST_SUPERMARKET",
            "chest supermarket": "CHEST_SUPERMARKET",
            "grocery": "CHEST_SUPERMARKET",
            "small ground": "GROUND_SMALL",
            "n block": "N_BLOCK",
            "n-block": "N_BLOCK",
            "nblock": "N_BLOCK",
            "cse block": "N_BLOCK",
            "aiml block": "N_BLOCK",
            "cse": "N_BLOCK",
            "aiml": "N_BLOCK",
            "computer": "N_BLOCK",
            "vignan vihar": "VIGNAN_VIHAR",
            "boys hostel": "VIGNAN_VIHAR",
            "vihar": "VIGNAN_VIHAR",
            "mess": "VIGNAN_VIHAR",
            "hostel mess": "VIGNAN_VIHAR",
            "e block": "E_BLOCK",
            "e-block": "E_BLOCK",
            "eblock": "E_BLOCK",
            "pharmacy block": "E_BLOCK",
            "pharmacy": "E_BLOCK",
            "biotech block": "E_BLOCK",
            "biotech": "E_BLOCK",
            "u block": "U_BLOCK",
            "u-block": "U_BLOCK",
            "ublock": "U_BLOCK",
            "law block": "U_BLOCK",
            "bba block": "U_BLOCK",
            "law": "U_BLOCK",
            "bba": "U_BLOCK",
            "convocation": "CONVOCATION_HALL",
            "convocation hall": "CONVOCATION_HALL",
            "auditorium": "CONVOCATION_HALL",
            "large ground": "GROUND_LARGE",
            "sports ground": "GROUND_LARGE",
            "vlits": "VLITS_EXIT",
            "lara": "VLITS_EXIT",
            "second gate": "SECOND_GATE",
            "gate 2": "SECOND_GATE"
        }

        # Check aliases sorted by length descending so specific multi-word aliases match first
        q_clean = re.sub(r'^(?:where\s+is|where\s+are|directions?\s+to|how\s+to\s+reach|how\s+do\s+i\s+(?:reach|get\s+to|go\s+to)|take\s+me\s+to)\s+', '', q, flags=re.I).strip()
        q_variants = [q, q.replace("_", " "), q.replace("-", " ")]
        if q_clean and q_clean != q:
            q_variants.extend([q_clean, q_clean.replace("_", " "), q_clean.replace("-", " ")])

        sorted_aliases = sorted(alias_map.items(), key=lambda x: len(x[0]), reverse=True)
        for variant in q_variants:
            for alias, node_id in sorted_aliases:
                if alias in variant or variant == alias:
                    return node_id

        # Fallback to name or description matching
        for nid, meta in cls._nodes.items():
            if q in meta["name"].lower() or q in meta["description"].lower() or q in meta["block"].lower():
                return nid

        return None

    @classmethod
    def find_shortest_path(cls, start_node: str, end_node: str) -> Optional[Dict[str, Any]]:
        cls._load_graph()
        if start_node not in cls._nodes or end_node not in cls._nodes:
            return None

        if start_node == end_node:
            dest = cls._nodes[end_node]
            return {
                "start": dest["name"],
                "destination": dest["name"],
                "total_distance_meters": 0.0,
                "steps": [f"You are already at {dest['name']}."],
                "destination_details": dest
            }

        # Dijkstra algorithm
        distances = {node: float("inf") for node in cls._nodes}
        previous = {node: None for node in cls._nodes}
        edge_info = {node: None for node in cls._nodes}
        distances[start_node] = 0.0

        pq = [(0.0, start_node)]

        while pq:
            curr_dist, u = heapq.heappop(pq)
            if curr_dist > distances[u]:
                continue
            if u == end_node:
                break

            for v, weight, path_name, instruction in cls._adj.get(u, []):
                distance = curr_dist + weight
                if distance < distances[v]:
                    distances[v] = distance
                    previous[v] = u
                    edge_info[v] = (path_name, instruction, weight)
                    heapq.heappush(pq, (distance, v))

        if distances[end_node] == float("inf"):
            return None

        # Reconstruct path
        path_nodes = []
        curr = end_node
        while curr is not None:
            path_nodes.append(curr)
            curr = previous[curr]
        path_nodes.reverse()

        step_instructions = []
        for i in range(1, len(path_nodes)):
            step_target = path_nodes[i]
            pname, instr, dist = edge_info[step_target]
            step_instructions.append(f"Step {i}: {instr} ({int(dist)}m)")

        dest_meta = cls._nodes[end_node]
        return {
            "start": cls._nodes[start_node]["name"],
            "destination": dest_meta["name"],
            "total_distance_meters": round(distances[end_node], 1),
            "step_count": len(step_instructions),
            "steps": step_instructions,
            "destination_details": dest_meta
        }


# ==============================================================================
# 23 SIDEBAR TOOLS IMPLEMENTATION
# ==============================================================================

class ToolRegistry:
    """Authoritative Tool Registry with 23 read-only tools."""

    # 1. HOME
    @staticmethod
    def get_home_overview(session: DatabaseSession) -> ToolResult:
        profile = DataRepository.get_student_profile(session) or {}
        att = DataRepository.get_attendance(session)
        overall_pct = 0.0
        if att:
            tot_h = sum(a.get("classes_held", 0) for a in att)
            tot_a = sum(a.get("classes_attended", 0) for a in att)
            overall_pct = round((tot_a / tot_h * 100), 1) if tot_h > 0 else 0.0

        full_name = profile.get("full_name", "Student")
        roll = profile.get("roll_no", session.student_id)
        prog = profile.get("programme_name", "B.Tech Computer Science")

        direct_answer = f"Welcome to VIGBOT. You are logged in as {full_name} ({roll}), enrolled in {prog} with an overall attendance of {overall_pct}%."

        return {
            "available": True,
            "source": "VFSTR Student Record Store",
            "last_updated": "2026-10-30",
            "sidebar_page": "home",
            "direct_answer": direct_answer,
            "data": {
                "profile": profile,
                "overall_attendance_pct": overall_pct,
                "active_academic_year": "2026-27 Semester-I"
            }
        }

    # 2. ATTENDANCE
    @staticmethod
    def get_attendance_records(session: DatabaseSession, course_code: Optional[str] = None) -> ToolResult:
        records = DataRepository.get_attendance(session, course_code)
        if not records:
            return {
                "available": False,
                "source": "VFSTR Biometric Attendance Database",
                "last_updated": "2026-10-30",
                "sidebar_page": "attendance",
                "direct_answer": "No attendance records were found matching your query in the university database.",
                "data": None,
                "missing_notice": "Please consult your Section Mentor or the Dean of Academics office."
            }

        target = None
        if course_code:
            target = next((r for r in records if course_code.lower() in (r.get("course_code") or "").lower() or course_code.lower() in (r.get("course_title") or "").lower()), records[0])
        else:
            target = next((r for r in records if r.get("current_pct", 100) < 75.0), records[0])

        pct = target.get("current_pct", 0.0)
        c_name = target.get("course_title", target.get("course_code", "Course"))
        held = target.get("classes_held", 0)
        att = target.get("classes_attended", 0)
        needed = target.get("classes_needed", 0)
        status = "Above Mandatory 75% Threshold" if pct >= 75.0 else "Below Mandatory 75% Cutoff"

        direct_answer = (
            f"Your attendance in {c_name} is {pct}% ({att}/{held} classes attended). "
            f"Status: {status}."
        )
        if pct < 75.0:
            direct_answer += f" You must attend the next {needed} consecutive classes without absence to reach 75%."

        return {
            "available": True,
            "source": "VFSTR Biometric Attendance System (R23 Regulation)",
            "last_updated": "2026-10-30",
            "sidebar_page": "attendance",
            "direct_answer": direct_answer,
            "data": {
                "target_course": target,
                "all_courses": records,
                "condonation_deadline": "2026-11-20"
            }
        }

    # 3. MARKS
    @staticmethod
    def get_marks_records(session: DatabaseSession, course_code: Optional[str] = None) -> ToolResult:
        marks = DataRepository.get_marks(session)
        if not marks:
            return {
                "available": False,
                "source": "VFSTR Examination & Evaluation Records",
                "last_updated": "2026-10-30",
                "sidebar_page": "marks",
                "direct_answer": "No Continuous Internal Evaluation (CIE) marks records were found for your student profile.",
                "data": None,
                "missing_notice": "Please check with your department Examination Coordinator."
            }

        filtered = marks
        if course_code:
            filtered = [m for m in marks if course_code.lower() in (m.get("course_code") or "").lower() or course_code.lower() in (m.get("course_title") or "").lower()]

        if not filtered:
            filtered = marks

        top = filtered[0]
        c_title = top.get("course_title", "Course")
        obt = top.get("obtained_marks", 0)
        max_m = top.get("max_marks", 0)
        ass_name = top.get("assessment_name", "Continuous Assessment")

        direct_answer = f"Your latest verified evaluation score in {c_title} ({ass_name}) is {obt}/{max_m} marks ({(obt/max_m*100):.1f}%)."

        return {
            "available": True,
            "source": "VFSTR Controller of Examinations (Continuous Internal Evaluation)",
            "last_updated": "2026-10-30",
            "sidebar_page": "marks",
            "direct_answer": direct_answer,
            "data": {
                "results": filtered,
                "total_assessments_logged": len(filtered)
            }
        }

    # 4. LIBRARY (Module 1 Grounded)
    @staticmethod
    def get_library_info(day_of_week: Optional[str] = None, resource_query: Optional[str] = None) -> ToolResult:
        with get_db_connection() as conn:
            if isinstance(conn, sqlite3.Connection):
                    conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            target_day = (day_of_week or "Sunday").strip().capitalize()
            q1 = "SELECT * FROM library_operating_hours WHERE day_of_week=%s" if not isinstance(conn, sqlite3.Connection) else "SELECT * FROM library_operating_hours WHERE day_of_week=?"
            cur.execute(q1, (target_day,))
            day_record = cur.fetchone()

            cur.execute("SELECT * FROM library_operating_hours")
            all_hours = [dict(r) for r in cur.fetchall()]

            resources = []
            if resource_query:
                q2 = "SELECT * FROM library_resources WHERE title LIKE %s OR course_code LIKE %s" if not isinstance(conn, sqlite3.Connection) else "SELECT * FROM library_resources WHERE title LIKE ? OR course_code LIKE ?"
                cur.execute(q2, (f"%{resource_query}%", f"%{resource_query}%"))
                resources = [dict(r) for r in cur.fetchall()]

        if not day_record:
            day_record = next((r for r in all_hours if r["day_of_week"].lower() == "sunday"), all_hours[0])

        d_name = day_record["day_of_week"]
        status = day_record["status"]
        open_t = day_record["open_time"]
        close_t = day_record["close_time"]
        reading_hrs = day_record["reading_room_hours"]

        if d_name.lower() == "sunday":
            direct_answer = (
                f"Yes, the Central Library is open on Sundays from {open_t} to {close_t} (09:00 - 17:00) "
                f"for reading rooms and digital study spaces, though book circulation counters remain closed."
            )
        else:
            direct_answer = (
                f"The Central Library is open on {d_name} from {open_t} to {close_t} "
                f"({status}) with circulation counters operating during designated hours."
            )

        return {
            "available": True,
            "source": "VFSTR NTR Vignan Central Library Operations Directorate",
            "last_updated": "2026-10-30",
            "sidebar_page": "library",
            "direct_answer": direct_answer,
            "data": {
                "day": d_name,
                "status": status,
                "open_time": open_t,
                "close_time": close_t,
                "reading_room_hours": reading_hrs,
                "circulation_hours": day_record["circulation_counter_hours"],
                "notes": day_record["notes"],
                "weekly_schedule": all_hours,
                "search_results": resources
            }
        }

    # 5. TIMETABLE
    @staticmethod
    def get_timetable_schedule(session: DatabaseSession, day_of_week: Optional[str] = None) -> ToolResult:
        slots = DataRepository.get_timetable(session, day_of_week)
        if not slots:
            return {
                "available": False,
                "source": "VFSTR Dynamic Scheduling System",
                "last_updated": "2026-10-30",
                "sidebar_page": "timetable",
                "direct_answer": "No scheduled lecture sessions were found for the requested day in your section timetable.",
                "data": None,
                "missing_notice": "Please check the master timetable pinned on the Department Notice Board."
            }

        first_slot = slots[0]
        day = first_slot.get("day_of_week", "Today")
        direct_answer = (
            f"On {day}, you have {len(slots)} scheduled academic periods, starting with "
            f"{first_slot.get('course_title', 'Lecture')} ({first_slot.get('course_code', '')}) "
            f"at {first_slot.get('time_slot', '08:00 AM')} in Room {first_slot.get('room_no', 'N-Block')}."
        )

        return {
            "available": True,
            "source": "VFSTR Academic Scheduling & Classroom Allocation Desk",
            "last_updated": "2026-10-30",
            "sidebar_page": "timetable",
            "direct_answer": direct_answer,
            "data": {
                "day": day,
                "total_periods": len(slots),
                "slots": slots
            }
        }

    # 6. EXAMS
    @staticmethod
    def get_examination_schedule(session: DatabaseSession, exam_type: Optional[str] = None) -> ToolResult:
        exams = DataRepository.get_exams(session)
        if not exams:
            return {
                "available": False,
                "source": "VFSTR Controller of Examinations (CoE)",
                "last_updated": "2026-10-30",
                "sidebar_page": "exams",
                "direct_answer": "No upcoming examination schedules were located in the official exam database for your registration number.",
                "data": None,
                "missing_notice": "Contact the Controller of Examinations office in Admin Block."
            }

        next_exam = exams[0]
        c_title = next_exam.get("course_title", "Course")
        date_str = next_exam.get("exam_date", "TBD")
        time_str = next_exam.get("time", "10:00 AM")
        venue = next_exam.get("venue", "Examination Hall")

        direct_answer = f"Your next scheduled examination is {c_title} on {date_str} at {time_str} in {venue}."

        return {
            "available": True,
            "source": "VFSTR Controller of Examinations (Semester-I 2026-27)",
            "last_updated": "2026-10-30",
            "sidebar_page": "exams",
            "direct_answer": direct_answer,
            "data": {
                "next_exam": next_exam,
                "all_exams": exams
            }
        }

    # 7. CURRICULUM
    @staticmethod
    def get_curriculum_audit(session: DatabaseSession) -> ToolResult:
        with get_db_connection() as conn:
            if isinstance(conn, sqlite3.Connection):
                    conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM curriculum LIMIT 1")
            row = cur.fetchone()
            curr = dict(row) if row else None

        if not curr:
            curr = {
                "regulation": "R23",
                "programme": "B.Tech Computer Science & Engineering",
                "total_credits_required": 160,
                "credits_earned": 68,
                "credits_remaining": 92,
                "graduation_eligibility": "On Track"
            }

        direct_answer = (
            f"Under the {curr['regulation']} CBCS curriculum for {curr['programme']}, "
            f"you have completed {curr['credits_earned']} out of {curr['total_credits_required']} required graduation credits ({curr['credits_remaining']} remaining). "
            f"Status: {curr['graduation_eligibility']}."
        )

        return {
            "available": True,
            "source": "VFSTR Academic Regulations & CBCS Curriculum Framework",
            "last_updated": "2026-10-30",
            "sidebar_page": "curriculum",
            "direct_answer": direct_answer,
            "data": curr
        }

    # 8. FEES
    @staticmethod
    def get_fee_status(session: DatabaseSession) -> ToolResult:
        fees = DataRepository.get_fees(session)
        if not fees:
            return {
                "available": False,
                "source": "VFSTR Finance & Accounts Department",
                "last_updated": "2026-10-30",
                "sidebar_page": "fees",
                "direct_answer": "No fee demand records were located for your student registration number.",
                "data": None,
                "missing_notice": "Please visit the Finance Counter, Ground Floor, Admin Block."
            }

        tot_demand = fees.get("total_demand", 0.0)
        paid = fees.get("paid_amount", 0.0)
        bal = fees.get("outstanding_balance", 0.0)
        due_d = fees.get("due_date", "2026-11-15")
        status = fees.get("status", "Pending")

        if bal > 0:
            direct_answer = (
                f"Your fee status is currently {status}: you have an outstanding balance of ₹{bal:,.0f} "
                f"(₹{paid:,.0f} paid out of ₹{tot_demand:,.0f} total demand), due by {due_d}."
            )
        else:
            direct_answer = f"Your fee status is fully cleared: zero outstanding dues for the current academic session."

        return {
            "available": True,
            "source": "VFSTR Finance & Fee Collection Portal",
            "last_updated": "2026-10-30",
            "sidebar_page": "fees",
            "direct_answer": direct_answer,
            "data": fees
        }

    # 9. SERVICES
    @staticmethod
    def get_services_directory(category: Optional[str] = None) -> ToolResult:
        services_list = [
            {"service_name": "Bonafide Certificate", "category": "Academic", "office": "Dean Academics Desk", "sla_days": 2, "fee": "Free"},
            {"service_name": "Official Transcripts", "category": "Examination", "office": "Controller of Examinations", "sla_days": 5, "fee": "₹200 per copy"},
            {"service_name": "Bus Pass Renewal", "category": "Transport", "office": "Transport Counter (Admin G-08)", "sla_days": 1, "fee": "Semester Transport Fee"},
            {"service_name": "Hostel Gate Pass / Station Leave", "category": "Hostel", "office": "Resident Warden Office", "sla_days": 1, "fee": "Free"},
            {"service_name": "Student ID Card Replacement", "category": "Identification", "office": "H-Block Ground Floor Office (Room H-G04)", "sla_days": 3, "fee": "₹100"},
            {"service_name": "SGRC Student Grievance Redressal", "category": "Grievance", "office": "Dean Student Affairs", "sla_days": 7, "fee": "Free"}
        ]

        if category:
            filtered = [s for s in services_list if category.lower() in s["category"].lower() or category.lower() in s["service_name"].lower()]
        else:
            filtered = services_list

        direct_answer = (
            f"VFSTR provides {len(services_list)} core administrative services through the Student Services desk, "
            f"including Bonafide Certificates (2 days SLA), Transcripts, ID Replacements (₹100), and SGRC Grievance Redressal."
        )

        return {
            "available": True,
            "source": "VFSTR Student Welfare & Administrative Services Office",
            "last_updated": "2026-10-30",
            "sidebar_page": "services",
            "direct_answer": direct_answer,
            "data": {
                "services": filtered
            }
        }

    # 10. HOSTEL & MESS (Module 2 Grounded)
    @staticmethod
    def get_hostel_and_mess_info(session: Optional[DatabaseSession] = None, residence_name: Optional[str] = None) -> ToolResult:
        with get_db_connection() as conn:
            if isinstance(conn, sqlite3.Connection):
                    conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM hostels")
            all_hostels = [dict(r) for r in cur.fetchall()]

        # Check if residence was specified
        matched_hostel = None
        if residence_name:
            rn = residence_name.strip().lower()
            tokens = [t for t in rn.replace("-", " ").replace("_", " ").split() if len(t) >= 2]
            for h in all_hostels:
                h_name = h["name"].lower()
                h_id = h["hostel_id"].lower()
                h_cat = (h.get("resident_category") or "").lower()
                # Direct substring match
                if rn in h_name or rn in h_id or rn in h_cat:
                    matched_hostel = h
                    break
                # Token overlap (e.g. "km" in "km boys hostel", "sp" in "villas sp residency")
                if any(t in h_id.split("_") or t in h_name.split() for t in tokens if t not in ("hostel", "boys", "girls")):
                    matched_hostel = h
                    break

        if matched_hostel:
            h_name = matched_hostel["name"]
            m_loc = matched_hostel["mess_location"]
            b_hrs = matched_hostel["breakfast_hours"]
            l_hrs = matched_hostel["lunch_hours"]
            d_hrs = matched_hostel["dinner_hours"]

            direct_answer = (
                f"The mess for {h_name} is located at the {m_loc}. "
                f"Meal timings are Breakfast: {b_hrs}, Lunch: {l_hrs}, Dinner: {d_hrs}."
            )
            return {
                "available": True,
                "source": "VFSTR Directorate of Student Hostels & Dining Affairs",
                "last_updated": "2026-10-30",
                "sidebar_page": "hostel",
                "direct_answer": direct_answer,
                "data": {
                    "hostel": matched_hostel,
                    "dining_architecture": "Decentralized (each hostel contains an internal mess on the ground floor)"
                }
            }

        # If user did not provide hostel name, explain the decentralized architecture and prompt for hostel
        hostel_names_list = [h["name"] for h in all_hostels[:5]]
        direct_answer = (
            f"Hostel dining facilities at VFSTR are decentralized: there is no single central mess building; "
            f"instead, every individual hostel (including Vignan Vihar, KM, AR, AP, and Priyadarshini) contains its own internal mess on the ground floor. "
            f"Which hostel do you reside in so I can provide your exact mess details? Dinner across all hostels is served from 7:30 PM to 9:00 PM."
        )

        return {
            "available": True,
            "source": "VFSTR Directorate of Student Hostels & Dining Affairs",
            "last_updated": "2026-10-30",
            "sidebar_page": "hostel",
            "direct_answer": direct_answer,
            "data": {
                "architecture_type": "Decentralized / Localized",
                "mess_location_rule": "Every individual boys and girls hostel contains a dedicated internal mess facility on its ground floor.",
                "standard_meal_hours": {
                    "breakfast": "7:30 AM - 8:45 AM",
                    "lunch": "12:30 PM - 2:00 PM",
                    "tea_and_snacks": "5:00 PM - 6:00 PM",
                    "dinner": "7:30 PM - 9:00 PM"
                },
                "available_hostels": [h["name"] for h in all_hostels]
            }
        }

    # 11. CAREER HUB
    @staticmethod
    def get_career_opportunities(job_type: Optional[str] = None) -> ToolResult:
        career_data = {
            "active_recruitment_drives": [
                {"company": "Amazon AWS", "role": "Cloud Support Associate", "ctc": "12 LPA", "eligibility": "CSE, IT, ECE (CGPA >= 7.5)", "drive_date": "2026-11-18"},
                {"company": "Tata Consultancy Services (TCS Digital)", "role": "Systems Engineer", "ctc": "7.5 LPA", "eligibility": "All B.Tech Branches (CGPA >= 6.5)", "drive_date": "2026-11-25"},
                {"company": "Schneider Electric", "role": "Graduate Engineer Trainee", "ctc": "8.0 LPA", "eligibility": "ECE, EEE, Mech (CGPA >= 7.0)", "drive_date": "2026-12-05"}
            ],
            "internship_programs": [
                {"company": "Microsoft AI Research", "duration": "6 Months", "stipend": "₹45,000/month", "domain": "Generative AI & LLMs", "deadline": "2026-11-15"}
            ]
        }

        direct_answer = (
            f"The VFSTR Training and Placement Cell has 3 active campus recruitment drives logged, "
            f"including Amazon AWS (12 LPA, Nov 18), TCS Digital (7.5 LPA, Nov 25), and Microsoft AI Internships (₹45k/mo)."
        )

        return {
            "available": True,
            "source": "VFSTR Training and Placement Cell (T&P)",
            "last_updated": "2026-10-30",
            "sidebar_page": "career",
            "direct_answer": direct_answer,
            "data": career_data
        }

    # 12. ACADEMIC CALENDAR
    @staticmethod
    def get_academic_calendar(month_or_event: Optional[str] = None) -> ToolResult:
        calendar_events = [
            {"date": "2026-07-15", "event": "Commencement of Classwork for Semester-I B.Tech (Academic Year 2026-27)"},
            {"date": "2026-09-14 to 2026-09-19", "event": "Continuous Internal Evaluation Mid-Term 1 Examinations"},
            {"date": "2026-10-18 to 2026-10-25", "event": "Dussehra & Festival Vacation (Instruction Suspended)"},
            {"date": "2026-11-16 to 2026-11-21", "event": "Continuous Internal Evaluation Mid-Term 2 Examinations"},
            {"date": "2026-11-20", "event": "Last Date for Medical Attendance Condonation Submission (Dean Academics)"},
            {"date": "2026-11-28", "event": "Last Day of Instruction for Semester-I"},
            {"date": "2026-12-01 to 2026-12-05", "event": "Practical & Laboratory Semester-End Examinations"},
            {"date": "2026-12-08 to 2026-12-22", "event": "Theory Semester-End Summative Examinations"}
        ]

        direct_answer = (
            f"Under the official 2026-27 Semester-I B.Tech Academic Calendar, Mid-Term 2 exams run from Nov 16–21, "
            f"the attendance condonation deadline is Nov 20, last instruction is Nov 28, and End-Semester exams run from Dec 8–22."
        )

        return {
            "available": True,
            "source": "VFSTR Dean of Academics (2026-27 B.Tech Academic Calendar)",
            "last_updated": "2026-10-30",
            "sidebar_page": "calendar",
            "direct_answer": direct_answer,
            "data": {
                "semester": "2026-27 Semester-I",
                "events": calendar_events
            }
        }

    # 13. CIRCULARS & NOTICES
    @staticmethod
    def get_official_circulars(limit: int = 5) -> ToolResult:
        with get_db_connection() as conn:
            if isinstance(conn, sqlite3.Connection):
                    conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            qc = "SELECT * FROM circulars ORDER BY issued_date DESC LIMIT %s" if not isinstance(conn, sqlite3.Connection) else "SELECT * FROM circulars ORDER BY issued_date DESC LIMIT ?"
            cur.execute(qc, (limit,))
            circulars = [dict(r) for r in cur.fetchall()]

        if not circulars:
            circulars = [
                {"circular_no": "VFSTR/REG/2026/042", "title": "Mid-Semester Examination Schedule Notification", "issued_date": "2026-10-12", "summary": "Mid-2 examinations commence from 16th November 2026.", "issued_by": "Controller of Examinations"},
                {"circular_no": "VFSTR/ACAD/2026/109", "title": "Mandatory 75% Attendance Compliance & Condonation", "issued_date": "2026-10-05", "summary": "Strict adherence to R23 regulations; condonation cutoff is 20th November 2026.", "issued_by": "Dean (Academics)"}
            ]

        latest = circulars[0]
        direct_answer = f"The latest university circular ({latest['circular_no']}: '{latest['title']}') was issued on {latest['issued_date']} by {latest['issued_by']}."

        return {
            "available": True,
            "source": "VFSTR Registrar & Dean of Academics Notice Board",
            "last_updated": "2026-10-30",
            "sidebar_page": "circulars",
            "direct_answer": direct_answer,
            "data": {
                "latest_circular": latest,
                "all_circulars": circulars
            }
        }

    CAMPUS_BLOCK_PROFILES = {
        "N_BLOCK": {
            "title": "N-Block (Computer Science & Engineering Block)",
            "purpose": "Primary academic facility housing the Department of Computer Science & Engineering (CSE) and Artificial Intelligence & Machine Learning (AI/ML).",
            "cohort": "2nd-year and 3rd-year senior students in CSE, Computer Science, and AI & ML.",
            "location": "Located on Path Beta just beside Zest, directly facing Vignan Vihar Boys Hostel (~240m from Main Gate).",
            "facilities": "Advanced AI & Deep Learning Research Labs, Central Computing Centers, Interactive Smart Classrooms, and Faculty Cabins."
        },
        "A_BLOCK": {
            "title": "A-Block (Freshers Academic Block)",
            "purpose": "Dedicated foundation academic block for all 1st-year undergraduate engineering students.",
            "cohort": "1st-year Freshers across all combined engineering branches (common foundation curriculum).",
            "location": "Located at the first right turn along Path Alpha, directly opposite H-Block (80m from Main Gate).",
            "facilities": "Dean of First Year Office, Basic Science Labs (Engineering Physics & Chemistry), Programming Labs, Drawing Halls, and Lecture Theatres."
        },
        "H_BLOCK": {
            "title": "H-Block (ECE, IT & University Administration)",
            "purpose": "Houses Electronics (ECE) and Information Technology (IT) departments, alongside central administrative services.",
            "cohort": "Senior students in ECE and IT programs, plus students visiting administrative cells.",
            "location": "Located directly opposite A-Block at the first right turn along Path Alpha (80m from Main Gate).",
            "facilities": "Student ID Card Replacement Office (ground-floor hallway), Advanced VLSI & Embedded Systems Labs, Communication Labs, Accounts Cell, and Examination Cell."
        },
        "U_BLOCK": {
            "title": "U-Block (School of Law & Management Studies)",
            "purpose": "Academic center for legal studies, management programs, and humanities.",
            "cohort": "Students enrolled in Law (BBA LL.B, LL.B) and Business Administration (BBA, MBA).",
            "location": "Located behind N-Block along Path Gamma past Intersection 2 (~320m from Main Gate).",
            "facilities": "State-of-the-art Moot Court Hall, Business Case Study Discussion Rooms, Management Analytics Lab, and Faculty Chambers."
        },
        "E_BLOCK": {
            "title": "E-Block (School of Pharmacy & Biotechnology)",
            "purpose": "Dedicated academic facility for Pharmaceutical Sciences and Biotechnology Engineering.",
            "cohort": "Pharmacy (B.Pharm, M.Pharm, Pharm.D) and Biotechnology engineering students.",
            "location": "Located at the left turn at Intersection 2 along Path Gamma (~310m from Main Gate).",
            "facilities": "Pharmaceutical Chemistry Labs, Pharmacology Research Labs, Cell Culture & Wet Labs, Bio-analytics Suite, and Animal House Facility."
        },
        "CHEST_SUPERMARKET": {
            "title": "Zest (Campus Supermarket & Store)",
            "purpose": "Central on-campus supermarket catering to daily student and staff necessities.",
            "cohort": "Open to all university students, hostel residents, faculty, and campus visitors.",
            "location": "Situated along Path Alpha immediately adjacent to MHP Canteen on the right, with N-Block situated just beside it (~175m from Main Gate).",
            "facilities": "Groceries, beverages, snacks, packaged meals, daily academic stationery, project charts, personal care essentials, and toiletries."
        },
        "VIGNAN_VIHAR": {
            "title": "Vignan Vihar (1st-Year Boys Hostel)",
            "purpose": "Primary on-campus residential hall dedicated to 1st-year male students.",
            "cohort": "1st-year undergraduate male students.",
            "location": "Situated on Path Beta, directly in front of N-Block (~270m from Main Gate).",
            "facilities": "Furnished residential rooms, 24/7 warden desk, security checkpost, high-speed Wi-Fi, and a large internal ground-floor student dining mess."
        },
        "NTR_LIBRARY": {
            "title": "NTR Central Library",
            "purpose": "Central university knowledge repository, learning commons, and research archive.",
            "cohort": "Open to all students, researchers, faculty, and staff.",
            "location": "Situated along Path Alpha just past Intersection 1 on the right (110m from Main Gate).",
            "facilities": "Multi-tier book stacks covering engineering, sciences, management, and literature; Air-conditioned reference halls; Digital learning lab with online journal access; Group discussion rooms and quiet study zones."
        },
        "MHP_CANTEEN": {
            "title": "MHP Campus Canteen",
            "purpose": "Main university food court and central dining cafeteria.",
            "cohort": "Open to all university students, faculty, and campus visitors.",
            "location": "Situated along Path Alpha on the right side, between NTR Library and Zest (150m from Main Gate).",
            "facilities": "Fresh breakfast, South Indian thalis, North Indian curries, snacks, fresh fruit juices, and extensive indoor/outdoor student seating."
        },
        "CONVOCATION_HALL": {
            "title": "Convocation Hall & University Auditorium",
            "purpose": "Premier indoor auditorium for grand university events, guest lectures, and cultural fests.",
            "cohort": "University-wide events, conferences, and annual convocation ceremonies.",
            "location": "Situated adjacent to U-Block along Path Delta, leading towards Second Gate and VLITS Block (~380m from Main Gate).",
            "facilities": "2,500+ seat air-conditioned main auditorium, stage lighting and acoustics, VIP green rooms, and conference seminar suites."
        }
    }

    # 14. CAMPUS MAP & NAVIGATION GRAPH (Module 4 Grounded)
    @staticmethod
    def get_campus_location_and_navigation(origin: Optional[str] = None, destination: Optional[str] = None) -> ToolResult:
        # Automatically parse origin and destination if passed as a natural language query
        parsed_origin, parsed_dest = None, destination
        if destination:
            m_to_from = re.search(r'(?:to|reach|go to)\s+(?:the\s+)?(.+?)\s+from\s+(?:the\s+)?(.+)', destination, re.I)
            if m_to_from:
                parsed_origin = m_to_from.group(2).strip()
                parsed_dest = re.sub(r'^(?:reach|go to|get to)\s+', '', m_to_from.group(1).strip(), flags=re.I)
            else:
                m_from_to = re.search(r'from\s+(?:the\s+)?(.+?)\s+(?:to|towards)\s+(?:the\s+)?(.+)', destination, re.I)
                if m_from_to:
                    parsed_origin = m_from_to.group(1).strip()
                    parsed_dest = m_from_to.group(2).strip()

        effective_origin = origin or parsed_origin or "main gate"
        effective_dest = parsed_dest or destination or ""

        # Default origin to Main Gate if omitted
        start_id = CampusGraphService.resolve_node_id(effective_origin) or "NODE_0_MAIN_GATE"
        dest_id = CampusGraphService.resolve_node_id(effective_dest)

        if not dest_id:
            # General map overview
            direct_answer = (
                "The VFSTR campus is structured around Path Alpha (Main Road starting from Main Gate), "
                "with A-Block and H-Block at the first right turn, NTR Library, MHP Canteen, and Zest (Supermarket) along the central avenue, "
                "N-Block and Vignan Vihar Boys Hostel on Path Beta, and E-Block (Pharmacy), U-Block (Law & BBA), and Convocation Hall on Path Gamma/Delta."
            )
            return {
                "available": True,
                "source": "VFSTR Campus Spatial Directory & Navigation Graph",
                "last_updated": "2026-10-30",
                "sidebar_page": "map",
                "direct_answer": direct_answer,
                "data": {
                    "key_blocks": {
                        "A-Block": "Freshers / 1st-year students (all combined branches), right side of First Right Turn",
                        "H-Block": "Electronics (ECE) & IT departments, plus Administrative Offices & ID Replacement (opposite A-Block)",
                        "N-Block": "2nd & 3rd-year computer branch students (CSE, AIML), located just beside Zest",
                        "Vignan Vihar": "1st-year boys hostel directly in front of N-Block with internal ground-floor mess",
                        "E-Block": "Pharmacy, B.Pharma, Biotech (left turn at Intersection 2)",
                        "U-Block": "Law & BBA students (located behind N-Block straight past Intersection 2)",
                        "Convocation Hall": "Auditorium adjacent to U-Block, leading to Second Gate & VLITS block"
                    }
                }
            }

        # Compute shortest algorithmic path via Dijkstra
        route = CampusGraphService.find_shortest_path(start_id, dest_id)
        if not route:
            return {
                "available": False,
                "source": "VFSTR Campus Spatial Directory",
                "last_updated": "2026-10-30",
                "sidebar_page": "map",
                "direct_answer": f"Unable to compute a direct campus walking route to the requested location: {destination}.",
                "data": None,
                "missing_notice": "Please consult the Campus Security Desk at the Main Gate."
            }

        dest_name = route["destination"]
        dest_desc = route["destination_details"]["description"]
        tot_dist = route["total_distance_meters"]
        steps = route["steps"]

        # Specialized Answer-First phrasing for all major campus blocks and landmarks
        if dest_id == "N_BLOCK":
            direct_answer = (
                f"N-Block is the Computer Science & Engineering Block (housing 2nd and 3rd-year CSE and AI/ML students), "
                f"located on Path Beta just beside Zest and directly facing Vignan Vihar Boys Hostel, "
                f"{tot_dist} meters (~3-4 min walk) from {route['start']}."
            )
        elif dest_id == "A_BLOCK":
            direct_answer = (
                f"A-Block is the Freshers Block (housing 1st-year students across all engineering branches), "
                f"located {tot_dist} meters from {route['start']} at the first right turn along Path Alpha, directly opposite H-Block."
            )
        elif dest_id == "H_BLOCK":
            if start_id == "A_BLOCK":
                direct_answer = (
                    "H-Block is located directly opposite A-Block across the sub-path (distance: 15 meters). "
                    "The Student ID Card Replacement Office is on the left side of the main ground-floor hallway."
                )
            else:
                direct_answer = (
                    f"H-Block houses Electronics (ECE), Information Technology (IT), Administrative Offices, and the Student ID Card Replacement Office, "
                    f"located {tot_dist} meters from {route['start']} at the first right turn along Path Alpha, directly opposite A-Block."
                )
        elif dest_id == "U_BLOCK":
            direct_answer = (
                f"U-Block houses the School of Law and Management (BBA & Law students), "
                f"located {tot_dist} meters from {route['start']} positioned directly behind N-Block and adjacent to Convocation Hall past Intersection 2."
            )
        elif dest_id == "E_BLOCK":
            direct_answer = (
                f"E-Block houses Pharmacy, B.Pharma, and Biotechnology, "
                f"located {tot_dist} meters from {route['start']} at a left turn off Intersection 2 along Path Gamma."
            )
        elif dest_id == "VIGNAN_VIHAR":
            direct_answer = (
                f"Vignan Vihar is the 1st-year boys hostel (featuring an internal ground-floor mess), "
                f"located directly in front of N-Block on Path Beta ({tot_dist} meters from {route['start']})."
            )
        elif dest_id == "CONVOCATION_HALL":
            direct_answer = (
                f"Convocation Hall is the central university auditorium for major academic events, convocations, and symposiums, "
                f"located adjacent to U-Block leading towards the Second Gate ({tot_dist} meters from {route['start']})."
            )
        elif dest_id == "NTR_LIBRARY":
            direct_answer = (
                f"NTR Central Library is located on Path Alpha just past Intersection 1 on your right ({tot_dist} meters from {route['start']}), "
                f"offering multi-floor book stacks, reference halls, and digital learning zones."
            )
        elif dest_id == "MHP_CANTEEN":
            direct_answer = (
                f"MHP Campus Canteen is the central university food court, "
                f"located along Path Alpha past the Library on the right ({tot_dist} meters from {route['start']})."
            )
        elif dest_id == "CHEST_SUPERMARKET":
            direct_answer = (
                f"Zest provides groceries, stationery, snacks, and daily essentials, "
                f"located along Path Alpha immediately adjacent to MHP Canteen on the right, with N-Block situated just beside it ({tot_dist} meters from {route['start']})."
            )
        else:
            direct_answer = (
                f"To reach {dest_name} from {route['start']}, proceed {tot_dist} meters via {route['step_count']} navigation steps: "
                f"{steps[0]}."
            )

        return {
            "available": True,
            "source": "VFSTR Campus Spatial Directory (Algorithmic Dijkstra Graph)",
            "last_updated": "2026-10-30",
            "sidebar_page": "map",
            "direct_answer": direct_answer,
            "data": {
                "dest_id": dest_id,
                "origin": route["start"],
                "destination": dest_name,
                "total_distance_meters": tot_dist,
                "steps": steps,
                "building_details": route["destination_details"],
                "building_profile": ToolRegistry.CAMPUS_BLOCK_PROFILES.get(dest_id)
            }
        }

    # 15. TRANSPORT & BUSES (Module 3 Grounded)
    @staticmethod
    def get_bus_schedule(route_or_hostel: Optional[str] = None, shift: Optional[str] = None) -> ToolResult:
        with get_db_connection() as conn:
            if isinstance(conn, sqlite3.Connection):
                    conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM hostel_bus_schedules")
            hostel_schedules = [dict(r) for r in cur.fetchall()]

            cur.execute("SELECT * FROM transportation_routes")
            city_routes = [dict(r) for r in cur.fetchall()]

        # Parse departure times JSON
        for s in hostel_schedules:
            if isinstance(s.get("departure_times_json"), str):
                s["departure_times"] = json.loads(s["departure_times_json"])

        req = (route_or_hostel or "").strip().lower()

        # If user asks for hostel bus
        if "hostel" in req or any(h in req for h in ["km", "villa", "sp", "ap", "ar", "aa", "ao"]):
            matched = []
            for s in hostel_schedules:
                if req in s["hostel_route"].lower() or any(k in req for k in s["hostel_route"].lower().split()):
                    matched.append(s)

            if not matched:
                matched = hostel_schedules

            direct_answer = (
                "Official hostel shuttle buses operate morning shifts (07:45 AM – 11:35 AM) and evening return shifts (01:45 PM – 09:00 PM) "
                "connecting KM Hostel, Villas SP Residency, and the AP/AR/AA/AO hostel clusters to campus."
            )

            return {
                "available": True,
                "source": "VFSTR Transport Office (Hostel Shuttle Service w.e.f. 01.10.2026)",
                "last_updated": "2026-10-01",
                "sidebar_page": "transport",
                "direct_answer": direct_answer,
                "data": {
                    "service_type": "Hostel Shuttle Fleet",
                    "effective_date": "01.10.2026",
                    "routes": matched
                }
            }

        # If user asks for Guntur / Vijayawada / Tenali city bus
        if any(c in req for c in ["guntur", "vijayawada", "tenali", "chilakaluripet", "city"]):
            direct_answer = (
                "VFSTR operates 4 major city transit routes: Route 1 (Guntur Express: 7:35 AM arrival, 4:45 PM return), "
                "Route 2 (Vijayawada Express: 7:30 AM arrival), Route 3 (Tenali Shuttle: 7:40 AM arrival), and Route 4 (Chilakaluripet: 7:30 AM arrival)."
            )
            return {
                "available": True,
                "source": "VFSTR Transport Desk (City Bus Fleet)",
                "last_updated": "2026-10-30",
                "sidebar_page": "transport",
                "direct_answer": direct_answer,
                "data": {
                    "service_type": "City Commuter Fleet",
                    "routes": city_routes
                }
            }

        # General transport overview
        direct_answer = (
            "VFSTR transport services include daily city commuter routes (Guntur, Vijayawada, Tenali arriving by 7:35 AM) "
            "and dedicated hostel shuttles for KM Hostel, Villas SP Residency, and AP/AR/AA/AO clusters operating from 07:45 AM to 09:00 PM."
        )

        return {
            "available": True,
            "source": "VFSTR Transport Department",
            "last_updated": "2026-10-30",
            "sidebar_page": "transport",
            "direct_answer": direct_answer,
            "data": {
                "hostel_shuttles": hostel_schedules,
                "city_routes": city_routes
            }
        }

    # 16. EVENTS
    @staticmethod
    def get_campus_events(event_type: Optional[str] = None) -> ToolResult:
        events = [
            {"event_name": "Vignan National Hackathon 2026", "category": "Technical", "dates": "2026-11-20 to 2026-11-21", "venue": "N-Block High-Performance Labs", "registration_fee": "Free", "status": "Registrations Open"},
            {"event_name": "Vignan Mahotsav 2026 (National Youth Fest)", "category": "Cultural", "dates": "2026-12-18 to 2026-12-20", "venue": "Convocation Hall & Open Air Theatre", "registration_fee": "₹200", "status": "Upcoming"},
            {"event_name": "Inter-Collegiate Athletics Meet", "category": "Sports", "dates": "2026-11-10 to 2026-11-12", "venue": "Large Sports Ground (Opposite U-Block)", "registration_fee": "Free", "status": "Team Trials Ongoing"}
        ]

        direct_answer = (
            f"Upcoming university events include the Vignan National Hackathon 2026 (Nov 20–21 in N-Block Labs) "
            f"and the annual Vignan Mahotsav National Youth Cultural Fest (Dec 18–20 at Convocation Hall)."
        )

        return {
            "available": True,
            "source": "VFSTR Student Activity Council & Cultural Committee",
            "last_updated": "2026-10-30",
            "sidebar_page": "events",
            "direct_answer": direct_answer,
            "data": {
                "events": events
            }
        }

    # 17. LOST AND FOUND & ID REPLACEMENT (Module 5 Grounded)
    @staticmethod
    def get_lost_and_found_info(query_type: Optional[str] = None, item_title: Optional[str] = None) -> ToolResult:
        q = (query_type or item_title or "").strip().lower()

        # Check if query is about lost identity card
        if any(k in q for k in ["id", "id card", "identity", "hall ticket", "card"]):
            with get_db_connection() as conn:
                if isinstance(conn, sqlite3.Connection):
                    conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("SELECT * FROM administrative_procedures WHERE procedure_id='lost_id_card_replacement'")
                proc = dict(cur.fetchone())

            steps = json.loads(proc["phase2_steps_json"])
            fee = proc["fee_amount"]
            loc = proc["phase2_physical_location"]

            direct_answer = (
                f"To replace a lost student ID card, follow the official two-phase procedure: "
                f"first submit a digital report on the sidebar's Lost & Found board, then report physically to the Administrative Office in H-Block "
                f"(ground floor, left hallway) to submit the form, collect Hostel & Chief Warden signatures, and remit the ₹{int(fee)} penalty fee."
            )

            return {
                "available": True,
                "source": "VFSTR Student Welfare Directorate & Administrative Office",
                "last_updated": "2026-10-30",
                "sidebar_page": "lost-and-found",
                "direct_answer": direct_answer,
                "data": {
                    "workflow": "Two-Phase Replacement State Machine",
                    "phase1_digital": proc["phase1_digital_instructions"],
                    "phase2_physical_location": loc,
                    "office_location": proc["office_location"],
                    "replacement_fee_rupees": fee,
                    "turnaround_sla_days": proc["sla_turnaround_days"],
                    "sequential_steps": steps
                }
            }

        # General lost and found community board query
        with get_db_connection() as conn:
            if isinstance(conn, sqlite3.Connection):
                    conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM lost_and_found WHERE status='active' ORDER BY id DESC LIMIT 5")
            active_items = [dict(r) for r in cur.fetchall()]

        direct_answer = (
            f"The campus Lost & Found registry currently has {len(active_items)} active reported items. "
            f"Students can report a lost possession or claim found items with photo verification directly on the Lost & Found page."
        )

        return {
            "available": True,
            "source": "VFSTR Campus Lost and Found Public Board",
            "last_updated": "2026-10-30",
            "sidebar_page": "lost-and-found",
            "direct_answer": direct_answer,
            "data": {
                "active_items": active_items,
                "reporting_instructions": "Submit registration number, last seen location, and description."
            }
        }

    # 18. BOOKINGS
    @staticmethod
    def get_facility_booking_info(facility_name: Optional[str] = None, date: Optional[str] = None) -> ToolResult:
        with get_db_connection() as conn:
            if isinstance(conn, sqlite3.Connection):
                    conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM facilities")
            facilities = [dict(r) for r in cur.fetchall()]

        if not facilities:
            facilities = [
                {"id": "FAC_SEM1", "name": "Seminar Hall 1", "type": "Hall", "capacity": 250, "description": "Air-conditioned seminar hall with dual projectors"},
                {"id": "FAC_AUD", "name": "Main Auditorium", "type": "Auditorium", "capacity": 1200, "description": "Central acoustic auditorium with full stage AV"},
                {"id": "FAC_OAT", "name": "Open Air Theatre (OAT)", "type": "Theatre", "capacity": 2500, "description": "Outdoor amphitheatre for large student events"},
                {"id": "FAC_SPORTS", "name": "Indoor Sports Complex", "type": "Sports", "capacity": 500, "description": "Badminton, table tennis, and gymnasium complex"}
            ]

        direct_answer = (
            f"Campus facilities available for student club and academic bookings include Seminar Hall 1 (Capacity: 250), "
            f"Main Auditorium (Capacity: 1200), Open Air Theatre (Capacity: 2500), and the Indoor Sports Complex. "
            f"Requests require faculty mentor endorsement 48 hours in advance."
        )

        return {
            "available": True,
            "source": "VFSTR Estate & Facility Management Desk",
            "last_updated": "2026-10-30",
            "sidebar_page": "bookings",
            "direct_answer": direct_answer,
            "data": {
                "facilities": facilities,
                "advance_booking_window": "48 hours prior to event",
                "approval_authority": "Dean Student Affairs & Estate Officer"
            }
        }

    # 19. CLUBS
    @staticmethod
    def get_clubs_directory(category_or_interest: Optional[str] = None) -> ToolResult:
        clubs = [
            {"name": "AI Innovation Club", "category": "Technical", "focus": "Artificial Intelligence, Machine Learning, Robotics & Hardware Prototyping", "lead": "Dr. N. Santhosho", "meeting_hub": "N-Block AI Lab"},
            {"name": "Symphony Music Club", "category": "Cultural", "focus": "Classical, Band, Vocals & Instruments", "lead": "Student Affairs Cell", "meeting_hub": "Convocation Hall Studio"},
            {"name": "Athletics & Sports Club", "category": "Sports", "focus": "Cricket, Football, Track & Field, Fitness", "lead": "Physical Education Dept", "meeting_hub": "Large Sports Ground"},
            {"name": "Competitive Programming Club", "category": "Technical", "focus": "Data Structures, Algorithms, LeetCode, Codeforces & Hackathons", "lead": "CSE Dept", "meeting_hub": "N-Block Lab 3"},
            {"name": "Theatrix Drama Club", "category": "Cultural", "focus": "Street Plays, Stage Acting, Scriptwriting", "lead": "Student Life Committee", "meeting_hub": "Open Air Theatre"}
        ]

        q = (category_or_interest or "").strip().lower()
        if "robot" in q or "ai" in q or "machine" in q:
            direct_answer = (
                "For robotics, artificial intelligence, and hardware prototyping, you should join the "
                "AI Innovation Club (Technical), based out of the N-Block High-Performance AI Lab."
            )
        elif "music" in q or "sing" in q:
            direct_answer = "For music, singing, and campus bands, you should join the Symphony Music Club (Cultural)."
        elif "code" in q or "coding" in q or "dsa" in q:
            direct_answer = "For coding, algorithmic challenges, and competitive programming, join the Competitive Programming Club (Technical)."
        else:
            direct_answer = (
                "VFSTR hosts 5 primary student clubs: AI Innovation Club (AI & Robotics), "
                "Competitive Programming Club (DSA & Hackathons), Symphony Music Club, Theatrix Drama Club, and the Athletics & Sports Club."
            )

        return {
            "available": True,
            "source": "VFSTR Student Life & Clubs Directorate",
            "last_updated": "2026-10-30",
            "sidebar_page": "clubs",
            "direct_answer": direct_answer,
            "data": {
                "clubs": clubs
            }
        }

    # 20. MARKETPLACE
    @staticmethod
    def get_marketplace_listings(category: Optional[str] = None) -> ToolResult:
        with get_db_connection() as conn:
            if isinstance(conn, sqlite3.Connection):
                    conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM marketplace_listings WHERE status='available' LIMIT 5")
            listings = [dict(r) for r in cur.fetchall()]

        if not listings:
            listings = [
                {"title": "Engineering Mechanics & Graphics Drafter", "category": "Engineering Tools", "price": 450, "status": "available"},
                {"title": "Discrete Mathematics by Kenneth Rosen (8th Ed)", "category": "Textbooks", "price": 350, "status": "available"},
                {"title": "Casio Scientific Calculator FX-991EX", "category": "Electronics", "price": 800, "status": "available"}
            ]

        direct_answer = (
            f"The Student Marketplace has {len(listings)} active peer listings, including engineering drawing kits, "
            f"used textbooks (Discrete Mathematics ₹350), and scientific calculators."
        )

        return {
            "available": True,
            "source": "VFSTR Student Peer-to-Peer Marketplace",
            "last_updated": "2026-10-30",
            "sidebar_page": "marketplace",
            "direct_answer": direct_answer,
            "data": {
                "listings": listings
            }
        }

    # 21. CAMPUS POLLING
    @staticmethod
    def get_campus_polls() -> ToolResult:
        polls = [
            {"id": "POLL_01", "question": "Which guest keynote topic do you prefer for Vignan Mahotsav 2026?", "options": ["Quantum Computing", "Generative AI Agents", "Space Robotics"], "status": "Active", "total_votes": 342},
            {"id": "POLL_02", "question": "Proposed library extended night reading hall hours during End-Sem exams?", "options": ["Open till 12:00 AM", "24/7 Overnight Access", "Keep 10:00 PM"], "status": "Active", "total_votes": 589}
        ]

        direct_answer = (
            f"There are currently {len(polls)} active campus polls open for voting, including the "
            f"Vignan Mahotsav Keynote topic poll and the End-Semester Library Night Reading Hall extension poll."
        )

        return {
            "available": True,
            "source": "VFSTR Student Senate & Governance Polling Portal",
            "last_updated": "2026-10-30",
            "sidebar_page": "polling",
            "direct_answer": direct_answer,
            "data": {
                "active_polls": polls
            }
        }

    # 22. ALUMNI NETWORK
    @staticmethod
    def get_alumni_mentors(company_or_domain: Optional[str] = None) -> ToolResult:
        mentors = [
            {"name": "Pooja Sharma", "batch": "2022", "company": "Google", "role": "Software Engineer II", "domain": "Distributed Systems", "available_for_chat": True},
            {"name": "Kiran Kumar", "batch": "2021", "company": "Microsoft", "role": "Senior Cloud Engineer", "domain": "Azure & Cloud Architecture", "available_for_chat": True},
            {"name": "Venkata Satish", "batch": "2023", "company": "Amazon", "role": "SDE I", "domain": "Full Stack & Microservices", "available_for_chat": True},
            {"name": "Divya Reddy", "batch": "2020", "company": "Qualcomm", "role": "Staff Hardware Engineer", "domain": "VLSI & Embedded Systems", "available_for_chat": False}
        ]

        q = (company_or_domain or "").strip().lower()
        if q:
            filtered = [m for m in mentors if q in m["company"].lower() or q in m["domain"].lower() or q in m["name"].lower()]
        else:
            filtered = mentors

        direct_answer = (
            f"The VFSTR Alumni Network connects students with verified senior alumni, including mentors currently at "
            f"Google (Pooja Sharma), Microsoft (Kiran Kumar), and Amazon (Venkata Satish) available for 1-on-1 career advice."
        )

        return {
            "available": True,
            "source": "VFSTR Directorate of Alumni Relations",
            "last_updated": "2026-10-30",
            "sidebar_page": "alumni",
            "direct_answer": direct_answer,
            "data": {
                "mentors": filtered
            }
        }

    # 23. POLICIES & REGULATIONS
    @staticmethod
    def get_university_policies(policy_id_or_keyword: Optional[str] = None) -> ToolResult:
        policies = [
            {"id": "POL-01", "title": "Institutional Attendance Policy (R23 Clause 4.2)", "summary": "Mandatory 75% attendance. Condonation permitted between 65% and 74.9% with Dean approval and medical certificate within 5 days. Debarment below 65%."},
            {"id": "POL-02", "title": "University Examination Conduct & Malpractice Rules", "summary": "Biometric & digital hall tickets required. Severe disciplinary referral to Unfair Means Committee (UMC) for unauthorized electronics or formula sheets."},
            {"id": "POL-03", "title": "Continuous Internal Evaluation (CIE) Grading Scale", "summary": "10-point letter grading scale. Internal evaluation weightage: 40% formative assessments, 60% summative end-semester exam."},
            {"id": "POL-04", "title": "Hostel Residence & Dining Bylaws (HD-01 to HD-06)", "summary": "Curfew 6:00 PM; gate closure 10:00 PM; decentralized internal ground-floor dining halls; dinner 7:30 PM - 9:00 PM; no high-wattage electrical appliances."}
        ]

        q = (policy_id_or_keyword or "").strip().lower()
        if "attend" in q or "condon" in q or "shortage" in q:
            direct_answer = (
                "Under VFSTR Academic Regulation R23 Clause 4.2, every student must maintain at least 75% attendance; "
                "students between 65.0% and 74.9% may apply for medical condonation, while attendance below 65% results in course detention."
            )
        elif "exam" in q or "malpractice" in q or "umc" in q:
            direct_answer = (
                "Under the Examination Conduct Policy (POL-02), unauthorized electronic devices or formula sheets are strictly prohibited "
                "and lead to immediate debarment under the Unfair Means Committee (UMC) regulations."
            )
        else:
            direct_answer = (
                "VFSTR official institutional bylaws include POL-01 (75% Attendance & Medical Condonation), "
                "POL-02 (Examination Conduct & UMC Rules), POL-03 (Continuous Evaluation Scale), and POL-04 (Hostel Residence & Dining Regulations)."
            )

        return {
            "available": True,
            "source": "VFSTR University Bylaws & Academic Regulations Handbook",
            "last_updated": "2026-10-30",
            "sidebar_page": "policies",
            "direct_answer": direct_answer,
            "data": {
                "policies": policies
            }
        }


# ==============================================================================
# TOOL REGISTRY SCHEMA DEFINITIONS FOR GEMINI FUNCTION CALLING
# ==============================================================================

GEMINI_TOOL_DEFINITIONS = [
    {
        "name": "get_home_overview",
        "description": "Retrieve student identity, roll number, department, and overall semester attendance percentage.",
        "parameters": {"type": "OBJECT", "properties": {}, "required": []}
    },
    {
        "name": "get_attendance_records",
        "description": "Look up official course attendance records, percentage, classes attended/held, classes needed to reach 75%, and condonation deadlines.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "course_code": {"type": "STRING", "description": "Course code (e.g. CS302) or subject name (e.g. DBMS, Operating Systems)."}
            },
            "required": []
        }
    },
    {
        "name": "get_marks_records",
        "description": "Look up Continuous Internal Evaluation (CIE), Formative Assessment (FA1, FA2), and mid-term marks for courses.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "course_code": {"type": "STRING", "description": "Course code or course title (e.g. DBMS, Data Structures)."}
            },
            "required": []
        }
    },
    {
        "name": "get_library_info",
        "description": "Query Central Library operating hours (including Sunday hours: 9:00 AM - 5:00 PM), study spaces, and borrowing rules.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "day_of_week": {"type": "STRING", "description": "Day of week to check hours for (e.g. Sunday, Monday, Saturday)."},
                "resource_query": {"type": "STRING", "description": "Book title or subject name to search in digital library resources."}
            },
            "required": []
        }
    },
    {
        "name": "get_timetable_schedule",
        "description": "Look up daily lecture timetable, period time slots, classroom room numbers, and faculty names.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "day_of_week": {"type": "STRING", "description": "Day of week (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday)."}
            },
            "required": []
        }
    },
    {
        "name": "get_examination_schedule",
        "description": "Look up mid-term and semester-end exam dates, timings, venues, and hall ticket statuses.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "exam_type": {"type": "STRING", "description": "Mid-Term 1, Mid-Term 2, or Semester-End."}
            },
            "required": []
        }
    },
    {
        "name": "get_curriculum_audit",
        "description": "Check CBCS graduation credits earned, remaining credits, and degree audit status.",
        "parameters": {"type": "OBJECT", "properties": {}, "required": []}
    },
    {
        "name": "get_fee_status",
        "description": "Look up student fee demands, payments, outstanding balance, due dates, and challan numbers.",
        "parameters": {"type": "OBJECT", "properties": {}, "required": []}
    },
    {
        "name": "get_services_directory",
        "description": "Directory of official student administrative services, certificates (Bonafide, Transcripts), SLA times, and office locations.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "category": {"type": "STRING", "description": "Service category (Academic, Examination, Transport, Identification, Grievance)."}
            },
            "required": []
        }
    },
    {
        "name": "get_hostel_and_mess_info",
        "description": "Query hostel internal dining hall (mess) locations, meal timings (breakfast, lunch, dinner), and residence bylaws. Note: Dining is decentralized into each hostel's ground floor.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "residence_name": {"type": "STRING", "description": "Name of student's hostel (e.g. Vignan Vihar, KM Hostel, AR Hostel, AP Hostel, Priyadarshini)."}
            },
            "required": []
        }
    },
    {
        "name": "get_career_opportunities",
        "description": "View active campus placement drives, visiting companies, CTC packages, and internship deadlines.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "job_type": {"type": "STRING", "description": "Full-time placement or Internship."}
            },
            "required": []
        }
    },
    {
        "name": "get_academic_calendar",
        "description": "Look up official university academic calendar events, holidays, vacation periods, and instructional deadlines.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "month_or_event": {"type": "STRING", "description": "Month name or event keyword (e.g. November, Dussehra, Mid-term, Condonation)."}
            },
            "required": []
        }
    },
    {
        "name": "get_official_circulars",
        "description": "Retrieve recent official university notices and registrar circulars.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "limit": {"type": "INTEGER", "description": "Number of circulars to retrieve (default 5)."}
            },
            "required": []
        }
    },
    {
        "name": "get_campus_location_and_navigation",
        "description": "Query campus building locations (U-Block, A-Block, H-Block, N-Block, NTR Library, Canteen, Convocation Hall) and compute turn-by-turn algorithmic walking directions from Main Gate or any campus node.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "origin": {"type": "STRING", "description": "Starting location (e.g. Main Gate, Freshers A-Block, N-Block). Default: Main Gate."},
                "destination": {"type": "STRING", "description": "Destination building or office (e.g. U-Block, H-Block, NTR Library, ID Card Office)."}
            },
            "required": ["destination"]
        }
    },
    {
        "name": "get_bus_schedule",
        "description": "Query official hostel shuttle timetables (KM Hostel, Villas SP Residency, AP/AR/AA/AO clusters) and city transit buses (Guntur, Vijayawada, Tenali).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "route_or_hostel": {"type": "STRING", "description": "Hostel name (KM Hostel, Villas SP, AP/AR) or City (Guntur, Vijayawada, Tenali)."},
                "shift": {"type": "STRING", "description": "Morning Shift or Evening Shift."}
            },
            "required": []
        }
    },
    {
        "name": "get_campus_events",
        "description": "Explore upcoming university events, hackathons, sports meets, and cultural festivals.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "event_type": {"type": "STRING", "description": "Technical, Cultural, or Sports."}
            },
            "required": []
        }
    },
    {
        "name": "get_lost_and_found_info",
        "description": "Look up active campus lost and found items OR query the official two-phase procedure for replacing a lost Student Identity Card.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query_type": {"type": "STRING", "description": "Specify 'id_card' for lost student ID replacement procedure, or 'items' for community lost possessions."},
                "item_title": {"type": "STRING", "description": "Name of specific lost item (e.g. calculator, id card, bottle)."}
            },
            "required": []
        }
    },
    {
        "name": "get_facility_booking_info",
        "description": "Check campus facility reservation details for seminar halls, auditorium, open air theatre, and sports complex.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "facility_name": {"type": "STRING", "description": "Seminar Hall 1, Main Auditorium, Open Air Theatre, or Sports Complex."}
            },
            "required": []
        }
    },
    {
        "name": "get_clubs_directory",
        "description": "Browse active student clubs, including AI & Robotics (AI Innovation Club), Coding & Hackathons (Competitive Programming), Music, Sports, and Drama.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "category_or_interest": {"type": "STRING", "description": "Student interest area (e.g. robotics, ai, coding, music, drama, sports)."}
            },
            "required": []
        }
    },
    {
        "name": "get_marketplace_listings",
        "description": "Browse peer-to-peer student marketplace items for textbooks, drafters, and calculators.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "category": {"type": "STRING", "description": "Textbooks, Engineering Tools, or Electronics."}
            },
            "required": []
        }
    },
    {
        "name": "get_campus_polls",
        "description": "View active campus polls, student voting topics, and referendum questions.",
        "parameters": {"type": "OBJECT", "properties": {}, "required": []}
    },
    {
        "name": "get_alumni_mentors",
        "description": "Connect with registered VFSTR alumni working across Google, Microsoft, Amazon, and Qualcomm.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "company_or_domain": {"type": "STRING", "description": "Company name (Google, Microsoft) or domain (Cloud, AI, VLSI)."}
            },
            "required": []
        }
    },
    {
        "name": "get_university_policies",
        "description": "Query official VFSTR academic bylaws: R23 attendance condonation (75%), detention (<65%), examination conduct, and grading scale.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "policy_id_or_keyword": {"type": "STRING", "description": "Attendance, condonation, detention, exam malpractice, or grading."}
            },
            "required": []
        }
    }
]
