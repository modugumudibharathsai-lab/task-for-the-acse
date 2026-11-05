import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from typing import List, Dict, Any, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.config import settings
from app.api import (
    auth_router,
    conversations_router,
    services_router,
    analytics_router,
    community_router,
    admin_router
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Backend service for **VIGBOT**.\n\n"
        "Provides authenticated, row-level secured access to student profiles, attendance, "
        "timetable, marks, examination schedules, fee demands, institutional policies, "
        "and administrative service requests with mid-conversation distress routing to Emergency Counseling."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

@app.on_event("startup")
async def on_startup():
    try:
        from app.db_init import init_postgres_schema
        init_postgres_schema()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"db_init startup error (non-fatal): {e}")


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register versioned routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(conversations_router, prefix=settings.API_V1_PREFIX)
app.include_router(services_router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics_router, prefix=settings.API_V1_PREFIX)
app.include_router(community_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)

from app.models.schemas import StudentProfile
from app.database import DataRepository, DatabaseSession
from app.security import get_current_student
from fastapi import Depends, HTTPException

@app.get("/api/v1/me", response_model=StudentProfile, tags=["Authentication"])
async def get_my_profile_v1(current_student: dict = Depends(get_current_student)):
    session = DatabaseSession(student_id=current_student["student_id"], user_id=current_student["user_id"])
    profile = DataRepository.get_student_profile(session)
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return StudentProfile(**profile)

@app.get("/api/v1/student/dashboard", tags=["Student"])
async def get_student_dashboard(current_student: dict = Depends(get_current_student)):
    session = DatabaseSession(student_id=current_student["student_id"], user_id=current_student["user_id"])
    profile = DataRepository.get_student_profile(session)
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    attendance = DataRepository.get_attendance(session)
    marks = DataRepository.get_marks(session)
    fees = DataRepository.get_fees(session)
    timetable = DataRepository.get_timetable(session)
    exams = DataRepository.get_exams(session)
    advisors = DataRepository.get_student_advisors(session)
    subject_faculty = DataRepository.get_subject_faculty(session)
    return {
        "profile": profile,
        "advisors": advisors,
        "faculty": subject_faculty,
        "attendance": attendance,
        "marks": marks,
        "fees": fees,
        "timetable": timetable,
        "exams": exams
    }

@app.get("/api/v1/student/faculty", response_model=dict, tags=["Student"])
async def get_my_faculty(current_student: dict = Depends(get_current_student)):
    session = DatabaseSession(student_id=current_student["student_id"], user_id=current_student["user_id"])
    advisors = DataRepository.get_student_advisors(session)
    if not advisors:
        raise HTTPException(status_code=404, detail="Student record not found")
    subject_faculty = DataRepository.get_subject_faculty(session)
    return {
        "student_id": current_student["student_id"],
        "roll_no": current_student.get("roll_no"),
        "advisors": advisors,
        "subject_faculty": subject_faculty
    }

@app.get("/api/v1/faculty", response_model=List[dict], tags=["Faculty Directory"])
async def list_faculty_directory():
    return DataRepository.get_faculty_directory()

@app.get("/api/v1/students", tags=["Student"])
async def list_students():
    from app.database import STUDENTS_DB
    return [
        {
            "roll_no": s["roll_no"],
            "full_name": s["full_name"],
            "cgpa": s["cgpa"],
            "overall_attendance_pct": s["overall_attendance_pct"],
            "backlog_count": s["backlog_count"],
            "fee_outstanding": s["fee_outstanding"],
            "status": s["status"]
        }
        for s in STUDENTS_DB.values()
    ]

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    def _usable_secret(secret: str) -> bool:
        return bool(secret and str(secret).strip() and not str(secret).startswith("YOUR_"))

    gemini_key = getattr(settings, "GEMINI_API_KEY", "")
    groq_key = getattr(settings, "GROQ_API_KEY", "")
    cloud_key = getattr(settings, "CLOUD_API_KEY", "")

    gemini_active = bool(getattr(settings, "ENABLE_GEMINI", False) and _usable_secret(gemini_key))
    groq_active = bool(getattr(settings, "ENABLE_GROQ", False) and (_usable_secret(groq_key) or _usable_secret(cloud_key) or _usable_secret(gemini_key)))

    provider = "gemini" if gemini_active else ("groq" if groq_active else "local")

    return {
        "status": "healthy",
        "agent": "VIGBOT (VIGBOT Agent)",
        "version": settings.APP_VERSION,
        "llm_provider": provider,
        "gemini_configured": gemini_active,
        "gemini_model": settings.GEMINI_MODEL,
        "groq_configured": groq_active,
        "rls_guardrail_enforced": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
