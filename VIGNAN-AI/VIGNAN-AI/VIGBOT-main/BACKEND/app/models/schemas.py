from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date

# ---------------- Auth Schemas ----------------
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    student_id: str
    roll_no: str
    full_name: str
    programme_code: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    student_id: Optional[str] = None
    roll_no: Optional[str] = None

class CheckStatusRequest(BaseModel):
    roll_no: str

class CheckStatusResponse(BaseModel):
    status: str  # 'activated' | 'unactivated' | 'unknown'
    masked_email: Optional[str] = None
    message: str

class RequestOtpRequest(BaseModel):
    roll_no: str
    purpose: Optional[str] = "ACTIVATION"

class RequestOtpResponse(BaseModel):
    success: bool
    message: str
    masked_email: Optional[str] = None
    expires_in_seconds: int = 600
    requires_admin_verification: bool = False

class VerifyAndActivateRequest(BaseModel):
    roll_no: str
    otp: str
    new_password: str
    confirm_password: str

class VerifyAndResetRequest(BaseModel):
    roll_no: str
    otp: str
    new_password: str
    confirm_password: str

class AccountActivationRequest(BaseModel):
    roll_no: str
    email: str
    new_password: str
    confirm_password: str

class PasswordResetRequest(BaseModel):
    roll_no: str
    email: str
    new_password: str
    confirm_password: str

class AuthActionResponse(BaseModel):
    success: bool
    message: str

# ---------------- Faculty & Advisor Schemas ----------------
class FacultyContact(BaseModel):
    name: str
    phone: str
    email: str
    cabin: Optional[str] = None
    designation: Optional[str] = None

class StudentAdvisors(BaseModel):
    class_teacher: FacultyContact
    counsellor: FacultyContact
    mentor: FacultyContact
    hod: Optional[FacultyContact] = None

class FacultyMember(BaseModel):
    faculty_id: str
    employee_no: str
    name: str
    designation: str
    department: str
    email: str
    phone: str
    cabin: str
    role: str
    office_hours: Optional[str] = None

class SubjectFacultyInfo(BaseModel):
    course_code: str
    course_title: str
    faculty_name: str
    phone: str
    email: str
    cabin: str
    designation: Optional[str] = None

class StudentFacultyResponse(BaseModel):
    student_id: str
    roll_no: str
    full_name: str
    advisors: StudentAdvisors
    subject_faculty: List[SubjectFacultyInfo]

# ---------------- Profile Schema ----------------
class StudentProfile(BaseModel):
    student_id: str
    roll_no: str
    full_name: str
    programme_code: str
    department_code: str
    batch_label: str
    section_code: str
    current_year_of_study: int
    cgpa: Optional[float] = None
    backlog_count: int = 0
    overall_attendance_pct: float
    fee_outstanding: float
    status: str
    # Faculty & Advisor Grounding
    class_teacher_name: Optional[str] = None
    class_teacher_phone: Optional[str] = None
    class_teacher_email: Optional[str] = None
    class_teacher_cabin: Optional[str] = None
    counsellor_name: Optional[str] = None
    counsellor_phone: Optional[str] = None
    counsellor_email: Optional[str] = None
    counsellor_cabin: Optional[str] = None
    mentor_name: Optional[str] = None
    mentor_phone: Optional[str] = None
    mentor_email: Optional[str] = None
    mentor_cabin: Optional[str] = None
    hod_name: Optional[str] = None
    hod_phone: Optional[str] = None
    hod_email: Optional[str] = None

# ---------------- Structured Card Schemas ----------------
class StructuredCard(BaseModel):
    type: str # 'attendance', 'exam', 'fee', 'curriculum', 'timetable', 'service', 'distress', 'policy', 'navigation'
    title: str
    subtitle: Optional[str] = None
    badge: Optional[str] = None
    badgeVariant: Optional[str] = "blue"
    data: Dict[str, Any] = Field(default_factory=dict)
    actionLabel: Optional[str] = None
    actionIntent: Optional[str] = None
    target: Optional[str] = None

# ---------------- Chat & Message Schemas ----------------
class MessageCreate(BaseModel):
    content: str
    language: Optional[str] = "en"
    selected_model: Optional[str] = "8B"

class Citation(BaseModel):
    title: str
    clause: str
    effective_date: str
    summary: Optional[str] = None

class MessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    sender_role: str
    content: str
    category: Optional[str] = None
    source_agent: Optional[str] = "VIGBOT"
    citations: List[Citation] = Field(default_factory=list)
    structured_card: Optional[StructuredCard] = None
    is_distress: bool = False
    suggested_follow_ups: List[str] = Field(default_factory=list)
    llm_provider: Optional[str] = "local"
    model_used: Optional[str] = None
    used_fallback: bool = False
    routed_by: Optional[str] = None
    redirect_path: Optional[str] = None
    action: Optional[Dict[str, Any]] = None
    created_at: datetime

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"

class ConversationResponse(BaseModel):
    conversation_id: str
    student_id: str
    title: str
    status: str
    created_at: datetime
    updated_at: datetime
    last_message: Optional[str] = None

class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse] = Field(default_factory=list)

# ---------------- Service Request Schemas ----------------
class ServiceRequestCreate(BaseModel):
    category: str # 'BONAFIDE_CERTIFICATE', 'GRADE_CARD_TRANSCRIPT', 'FEE_CONCESSION', 'HOSTEL_MAINTENANCE', 'ID_CARD_REPLACEMENT', 'BUS_PASS_ENDORSEMENT', 'MENTOR_MEETING', 'GRIEVANCE', 'OTHER'
    title: str
    description: str
    priority: Optional[str] = "NORMAL"

class ServiceRequestResponse(BaseModel):
    service_request_id: str
    request_no: str
    student_id: str
    category: str
    title: str
    description: str
    priority: str
    status: str
    assigned_office: str
    sla_due_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

# ---------------- Human Handover Schema ----------------
class HandoverCreate(BaseModel):
    conversation_id: Optional[str] = None
    target_office: str
    reason: str
    conversation_summary: str
    urgency: Optional[str] = "NORMAL"

class HandoverResponse(BaseModel):
    handover_id: str
    handover_no: str
    student_id: str
    target_office: str
    reason: str
    urgency: str
    status: str
    created_at: datetime

# ---------------- Analytics Schema ----------------
class DailyAnalyticsItem(BaseModel):
    stat_date: str
    intent_category: str
    topic: str
    language_code: str
    query_count: int
    successful_answers: int
    escalated_count: int
    distress_count: int

# ---------------- Feedback & 8B Training Schemas ----------------
class MessageFeedbackCreate(BaseModel):
    rating: str  # "up" or "down"
    comment: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None
    response_text: Optional[str] = None

class MessageFeedbackResponse(BaseModel):
    status: str
    saved_for_training: bool
    rating: str
    message: str
