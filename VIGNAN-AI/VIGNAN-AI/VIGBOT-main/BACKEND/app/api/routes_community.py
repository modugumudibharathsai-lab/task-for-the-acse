import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status, Depends
from pydantic import BaseModel, Field
from app.database import DataRepository, get_db_connection
from app.security import get_current_student, verify_student_access

router = APIRouter(prefix="/community", tags=["Campus Community & Services"])


# -------------------------------------------------------------
# Pydantic Schemas
# -------------------------------------------------------------
class LostAndFoundReport(BaseModel):
    student_id: str
    type: str = Field(..., description="'lost' or 'found'")
    title: str
    description: str
    tags: Optional[str] = ""
    contact_info: str
    image_url: Optional[str] = None


class LostAndFoundClaim(BaseModel):
    student_id: str


class MarketplaceListingCreate(BaseModel):
    student_id: str
    title: str
    category: str
    price: float


class BookingCreate(BaseModel):
    facility_id: int
    student_id: str
    date: str
    start_time: str
    end_time: str
    purpose: str


class EventRegistrationCreate(BaseModel):
    student_id: str
    event_name: str


class HostelRequestCreate(BaseModel):
    student_id: str
    type: str
    details: str


# -------------------------------------------------------------
# Helper for safe insert returning
# -------------------------------------------------------------
def _execute_insert_and_commit(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    import sqlite3
    with get_db_connection() as conn:
        if isinstance(conn, sqlite3.Connection):
            cur = conn.execute(query, params)
            conn.commit()
            if "RETURNING" in query.upper():
                return [dict(row) for row in cur.fetchall()]
            return []
        else:
            query_pg = query.replace("?", "%s")
            with conn.cursor() as cur:
                cur.execute(query_pg, params)
                res = []
                if "RETURNING" in query.upper():
                    res = [dict(row) for row in cur.fetchall()]
            conn.commit()
            return res


# -------------------------------------------------------------
# Lost & Found Endpoints
# -------------------------------------------------------------
@router.get("/lost-and-found")
async def get_lost_and_found(filter_type: str = Query("all", pattern="^(all|lost|found)$")):
    """
    Fetch open Lost & Found items from Neon PostgreSQL.
    Publicly accessible campus-wide so all students see reported items.
    """
    try:
        if filter_type in ("lost", "found"):
            query = "SELECT * FROM lost_and_found WHERE status = 'open' AND type = ? ORDER BY date_posted DESC"
            items = DataRepository._execute_query(query, (filter_type,))
        else:
            query = "SELECT * FROM lost_and_found WHERE status = 'open' ORDER BY date_posted DESC"
            items = DataRepository._execute_query(query)
        return {"success": True, "items": items}
    except Exception as e:
        return {"success": False, "error": str(e), "items": []}


@router.post("/lost-and-found")
async def report_lost_and_found(item: LostAndFoundReport):
    """
    Report a new Lost or Found item directly to Neon PostgreSQL.
    Immediately visible to all students across the university.
    """
    try:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        insert_query = """
            INSERT INTO lost_and_found (student_id, type, title, description, tags, contact_info, status, date_posted, image_url)
            VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?)
            RETURNING id, student_id, type, title, description, tags, contact_info, status, date_posted, image_url
        """
        rows = _execute_insert_and_commit(
            insert_query,
            (
                item.student_id,
                item.type.lower(),
                item.title,
                item.description,
                item.tags or "",
                item.contact_info,
                now_iso,
                item.image_url
            )
        )
        new_id = rows[0]["id"] if rows else None
        return {"success": True, "id": new_id, "item": rows[0] if rows else None}
    except Exception as e:
        return {"success": False, "error": f"Failed to report item: {str(e)}"}


@router.post("/lost-and-found/{item_id}/claim")
async def claim_lost_and_found(item_id: int, claim: LostAndFoundClaim):
    """
    Mark an item as claimed in Neon PostgreSQL.
    """
    try:
        # Check if item exists
        items = DataRepository._execute_query("SELECT * FROM lost_and_found WHERE id = ?", (item_id,))
        if not items:
            return {"success": False, "error": "Item not found"}
        
        update_query = "UPDATE lost_and_found SET status = 'claimed' WHERE id = ?"
        _execute_insert_and_commit(update_query, (item_id,))
        return {"success": True, "message": f"Item {item_id} marked as claimed by student {claim.student_id}"}
    except Exception as e:
        return {"success": False, "error": f"Failed to claim item: {str(e)}"}


# -------------------------------------------------------------
# Marketplace Endpoints
# -------------------------------------------------------------
@router.get("/marketplace")
async def get_marketplace():
    """
    Fetch all active marketplace listings from Neon PostgreSQL.
    """
    try:
        listings = DataRepository._execute_query("SELECT * FROM marketplace_listings ORDER BY created_at DESC")
        return {"success": True, "data": listings}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}


@router.post("/marketplace")
async def create_marketplace_listing(
    listing: MarketplaceListingCreate,
    current_student: dict = Depends(get_current_student)
):
    """
    Add a new marketplace item to Neon PostgreSQL so any student can purchase/view.
    """
    verify_student_access(current_student, listing.student_id)
    try:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        insert_query = """
            INSERT INTO marketplace_listings (student_id, title, category, price, status, created_at)
            VALUES (?, ?, ?, ?, 'Available', ?)
            RETURNING id
        """
        rows = _execute_insert_and_commit(
            insert_query,
            (listing.student_id, listing.title, listing.category, listing.price, now_iso)
        )
        new_id = rows[0]["id"] if rows else None
        return {"success": True, "id": new_id}
    except Exception as e:
        return {"success": False, "error": f"Failed to create listing: {str(e)}"}


# -------------------------------------------------------------
# Facilities & Bookings Endpoints
# -------------------------------------------------------------
@router.get("/facilities")
async def get_facilities():
    try:
        facilities = DataRepository._execute_query("SELECT * FROM facilities ORDER BY id ASC")
        return {"success": True, "facilities": facilities}
    except Exception as e:
        return {"success": False, "error": str(e), "facilities": []}


@router.get("/bookings")
async def get_bookings(facility_id: Optional[int] = None, date: Optional[str] = None):
    try:
        if facility_id and date:
            bookings = DataRepository._execute_query(
                "SELECT * FROM bookings WHERE facility_id = ? AND date = ? AND status = 'confirmed'",
                (facility_id, date)
            )
        else:
            bookings = DataRepository._execute_query("SELECT * FROM bookings WHERE status = 'confirmed' ORDER BY date ASC")
        return {"success": True, "bookings": bookings}
    except Exception as e:
        return {"success": False, "error": str(e), "bookings": []}


@router.post("/bookings")
async def create_facility_booking(
    booking: BookingCreate,
    current_student: dict = Depends(get_current_student)
):
    verify_student_access(current_student, booking.student_id)
    try:
        insert_query = """
            INSERT INTO bookings (facility_id, student_id, date, start_time, end_time, purpose, status)
            VALUES (?, ?, ?, ?, ?, ?, 'confirmed')
            RETURNING id
        """
        rows = _execute_insert_and_commit(
            insert_query,
            (booking.facility_id, booking.student_id, booking.date, booking.start_time, booking.end_time, booking.purpose)
        )
        new_id = rows[0]["id"] if rows else None
        return {"success": True, "id": new_id}
    except Exception as e:
        return {"success": False, "error": f"Failed to create booking: {str(e)}"}


# -------------------------------------------------------------
# Campus Polls Endpoints
# -------------------------------------------------------------
@router.get("/polls")
async def get_polls():
    try:
        polls = DataRepository._execute_query("SELECT * FROM campus_polls WHERE is_active = 1 OR is_active = true ORDER BY id DESC")
        return {"success": True, "polls": polls}
    except Exception as e:
        return {"success": False, "error": str(e), "polls": []}


# -------------------------------------------------------------
# Campus Broadcasts & Alerts
# -------------------------------------------------------------
@router.get("/broadcasts")
async def get_broadcasts():
    try:
        broadcasts = DataRepository._execute_query("SELECT * FROM broadcast_alerts WHERE is_active = 1 OR is_active = true ORDER BY timestamp DESC")
        return {"success": True, "broadcasts": broadcasts}
    except Exception as e:
        return {"success": False, "error": str(e), "broadcasts": []}


# -------------------------------------------------------------
# Campus Locations & Transportation
# -------------------------------------------------------------
@router.get("/locations")
async def get_locations():
    try:
        locations = DataRepository._execute_query("SELECT * FROM campus_locations")
        return {"success": True, "locations": locations}
    except Exception as e:
        return {"success": False, "error": str(e), "locations": []}


@router.get("/transport")
async def get_transport():
    try:
        routes = DataRepository._execute_query("SELECT * FROM transportation_routes")
        return {"success": True, "routes": routes}
    except Exception as e:
        return {"success": False, "error": str(e), "routes": []}


# -------------------------------------------------------------
# Wellness & Alumni
# -------------------------------------------------------------
@router.get("/wellness")
async def get_wellness():
    try:
        resources = DataRepository._execute_query("SELECT * FROM wellness_resources")
        return {"success": True, "resources": resources}
    except Exception as e:
        return {"success": False, "error": str(e), "resources": []}


@router.get("/alumni")
async def get_alumni():
    try:
        mentors = DataRepository._execute_query("SELECT * FROM alumni_mentors")
        return {"success": True, "mentors": mentors}
    except Exception as e:
        return {"success": False, "error": str(e), "mentors": []}


@router.get("/library")
async def get_library():
    try:
        resources = DataRepository._execute_query("SELECT * FROM library_resources")
        return {"success": True, "resources": resources}
    except Exception as e:
        return {"success": False, "error": str(e), "resources": []}


# -------------------------------------------------------------
# Events Registration
# -------------------------------------------------------------
@router.get("/events")
async def get_events(student_id: Optional[str] = None):
    try:
        if student_id:
            events = DataRepository._execute_query("SELECT * FROM event_registrations WHERE student_id = ?", (student_id,))
        else:
            events = DataRepository._execute_query("SELECT * FROM event_registrations")
        return {"success": True, "events": events}
    except Exception as e:
        return {"success": False, "error": str(e), "events": []}


@router.post("/events/register")
async def register_event(
    reg: EventRegistrationCreate,
    current_student: dict = Depends(get_current_student)
):
    verify_student_access(current_student, reg.student_id)
    try:
        qr = f"QR-{reg.student_id}-{int(datetime.datetime.now().timestamp())}"
        rows = _execute_insert_and_commit(
            "INSERT INTO event_registrations (student_id, event_name, qr_code, status) VALUES (?, ?, ?, 'Registered') RETURNING id",
            (reg.student_id, reg.event_name, qr)
        )
        return {"success": True, "id": rows[0]["id"] if rows else None}
    except Exception as e:
        return {"success": False, "error": str(e)}


# -------------------------------------------------------------
# Hostel Management
# -------------------------------------------------------------
@router.get("/hostel")
async def get_hostel_requests(
    student_id: Optional[str] = None,
    current_student: dict = Depends(get_current_student)
):
    try:
        sid = current_student["student_id"]
        requests = DataRepository._execute_query(
            "SELECT * FROM hostel_requests WHERE student_id = ? OR student_id = ? ORDER BY created_at DESC",
            (sid, current_student.get("roll_no"))
        )
        return {"success": True, "requests": requests}
    except Exception as e:
        return {"success": False, "error": str(e), "requests": []}


@router.post("/hostel")
async def create_hostel_request(
    req: HostelRequestCreate,
    current_student: dict = Depends(get_current_student)
):
    verify_student_access(current_student, req.student_id)
    try:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        rows = _execute_insert_and_commit(
            "INSERT INTO hostel_requests (student_id, type, details, status, created_at) VALUES (?, ?, ?, 'Pending', ?) RETURNING id",
            (req.student_id, req.type, req.details, now_iso)
        )
        return {"success": True, "id": rows[0]["id"] if rows else None}
    except Exception as e:
        return {"success": False, "error": str(e)}
