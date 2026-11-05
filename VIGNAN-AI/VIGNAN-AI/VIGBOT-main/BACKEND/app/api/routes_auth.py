import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from app.config import settings
from app.models.schemas import (
    LoginRequest,
    Token,
    StudentProfile,
    CheckStatusRequest,
    CheckStatusResponse,
    RequestOtpRequest,
    RequestOtpResponse,
    VerifyAndActivateRequest,
    VerifyAndResetRequest,
    AccountActivationRequest,
    PasswordResetRequest,
    AuthActionResponse
)
from app.database import DataRepository, DatabaseSession
from app.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_student,
    is_hash_cryptographic,
    mask_email,
    generate_otp_hash,
    verify_otp_hash
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

UNIFORM_AUTH_ERROR = "Invalid registration number or password."


def validate_password_strength(password: str, roll_no: Optional[str] = None) -> None:
    """Enforces minimum security strength for student passwords."""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long."
        )
    if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one letter and one number."
        )
    if roll_no and password.strip().upper() == roll_no.strip().upper():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password cannot be your registration number."
        )


@router.post("/check-status", response_model=CheckStatusResponse)
async def check_student_status(req: CheckStatusRequest):
    """
    Checks whether a student registration number is eligible and activated.
    Emits uniform generic responses for unapproved accounts to prevent account enumeration.
    """
    clean_roll = req.roll_no.strip().upper()
    student = DataRepository.get_student_by_username(clean_roll)
    
    # Must be present in approved institutional records (genuine VFSTR 251FA... series)
    if not student or not clean_roll.startswith("251FA"):
        return CheckStatusResponse(
            status="unknown",
            masked_email=None,
            message="If this registration number belongs to an active VFSTR student, please verify your details or contact the helpdesk."
        )
    
    stored_hash = student.get("password_hash") or ""
    is_activated = is_hash_cryptographic(stored_hash)
    email = student.get("email") or ""
    masked = mask_email(email)
    
    if is_activated:
        return CheckStatusResponse(
            status="activated",
            masked_email=masked,
            message="Account is active. Please enter your password to sign in."
        )
    else:
        return CheckStatusResponse(
            status="unactivated",
            masked_email=masked,
            message="Account has not been activated yet. Please proceed with identity verification."
        )


@router.post("/activation/request-otp", response_model=RequestOtpResponse)
async def request_activation_otp(req: RequestOtpRequest):
    """
    Dispatches a single-use, time-limited 6-digit OTP to the student's verified institutional email.
    Enforces rate-limiting (3 requests per 15 minutes) and rejects duplicate activations.
    """
    clean_roll = req.roll_no.strip().upper()
    student = DataRepository.get_student_by_username(clean_roll)
    
    # Must be an approved institutional student
    if not student or not clean_roll.startswith("251FA"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student registration number not found in approved institutional records."
        )
    
    # Check if already activated
    stored_hash = student.get("password_hash") or ""
    if is_hash_cryptographic(stored_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account has already been activated. Please sign in with your password, or use password reset."
        )
    
    # Rate limit check (max 3 per 15 minutes)
    if not DataRepository.check_otp_rate_limit(clean_roll, window_minutes=15, max_requests=3):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many verification requests. Please wait 15 minutes before requesting a new code."
        )
    
    registered_email = (student.get("email") or "").strip().lower()
    if not registered_email:
        # Record case for manual admin verification
        DataRepository.record_manual_verification(
            clean_roll,
            student.get("full_name", ""),
            "No verified contact details on institutional record"
        )
        return RequestOtpResponse(
            success=False,
            requires_admin_verification=True,
            message="No verified institutional contact is on record for this student. A verification request has been forwarded to the Dean Student Affairs for manual verification.",
            masked_email=None,
            expires_in_seconds=0
        )
    
    # Generate cryptographically random 6-digit OTP
    otp = "".join(secrets.choice("0123456789") for _ in range(6))
    otp_hash = generate_otp_hash(otp, clean_roll, settings.SECRET_KEY)
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    
    DataRepository.save_otp(clean_roll, otp_hash, "ACTIVATION", expires_at)
    
    # Dispatch email to verified institutional address
    subject = "VIGNAN-AI Account Activation Verification Code"
    body = (
        f"Hello {student.get('full_name', 'Student')},\n\n"
        f"Your 6-digit VIGNAN-AI account activation code is: {otp}\n\n"
        f"This code will expire in 10 minutes.\n"
        f"If you did not request this verification, please contact the VFSTR Helpdesk immediately.\n\n"
        f"Vignan Foundation for Science, Technology and Research"
    )
    DataRepository.dispatch_student_email(registered_email, clean_roll, subject, body)
    
    masked = mask_email(registered_email)
    return RequestOtpResponse(
        success=True,
        message=f"A 6-digit verification code has been dispatched to your institutional email ({masked}). Valid for 10 minutes.",
        masked_email=masked,
        expires_in_seconds=600,
        requires_admin_verification=False
    )


@router.post("/activation/verify-and-activate", response_model=Token)
async def verify_otp_and_activate(req: VerifyAndActivateRequest):
    """
    Verifies the OTP, enforces attempt limits, sets strong salted password hash,
    and returns an authenticated student session.
    """
    clean_roll = req.roll_no.strip().upper()
    student = DataRepository.get_student_by_username(clean_roll)
    
    if not student or not clean_roll.startswith("251FA"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student registration number not found in approved institutional records."
        )
    
    stored_hash = student.get("password_hash") or ""
    if is_hash_cryptographic(stored_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account has already been activated. Please sign in with your password."
        )
    
    if req.new_password != req.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation password do not match."
        )
    
    validate_password_strength(req.new_password, clean_roll)
    
    # Fetch active OTP record
    otp_record = DataRepository.get_active_otp(clean_roll, "ACTIVATION")
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending verification code found. Please request a new code."
        )
    
    # Check expiry
    try:
        exp_dt = datetime.fromisoformat(otp_record["expires_at"])
        if exp_dt.tzinfo is None:
            exp_dt = exp_dt.replace(tzinfo=timezone.utc)
    except Exception:
        exp_dt = datetime.now(timezone.utc) - timedelta(seconds=1)
        
    if datetime.now(timezone.utc) > exp_dt:
        DataRepository.mark_otp_used(otp_record["id"])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please request a new code."
        )
    
    attempts_left = otp_record.get("attempts_left", 3)
    if attempts_left <= 0:
        DataRepository.mark_otp_used(otp_record["id"])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum verification attempts exceeded. Please request a new code."
        )
    
    # Constant-time comparison
    is_valid = verify_otp_hash(req.otp, clean_roll, settings.SECRET_KEY, otp_record["otp_hash"])
    if not is_valid:
        new_attempts = attempts_left - 1
        is_used = 1 if new_attempts <= 0 else 0
        DataRepository.update_otp_attempts(otp_record["id"], new_attempts, is_used)
        if new_attempts <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum verification attempts exceeded. Please request a new code."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid verification code. Attempts remaining: {new_attempts}"
        )
    
    # Invalidate OTP immediately to prevent reuse
    DataRepository.mark_otp_used(otp_record["id"])
    
    # Hash password with OWASP PBKDF2-HMAC-SHA256 (100,000 iterations)
    secure_hash = get_password_hash(req.new_password)
    DataRepository.update_student_password(clean_roll, secure_hash)
    
    # Issue authenticated JWT
    token_payload = {
        "sub": student["user_id"],
        "student_id": student["student_id"],
        "roll_no": student["roll_no"],
        "full_name": student["full_name"],
        "programme_code": student["programme_code"],
        "role": "student"
    }
    token = create_access_token(token_payload)
    
    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=86400,
        student_id=student["student_id"],
        roll_no=student["roll_no"],
        full_name=student["full_name"],
        programme_code=student["programme_code"]
    )


@router.post("/password-reset/request-otp", response_model=RequestOtpResponse)
async def request_password_reset_otp(req: RequestOtpRequest):
    """
    Dispatches a single-use OTP for password reset to an activated student's email.
    """
    clean_roll = req.roll_no.strip().upper()
    student = DataRepository.get_student_by_username(clean_roll)
    
    if not student or not clean_roll.startswith("251FA"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student registration number not found."
        )
    
    stored_hash = student.get("password_hash") or ""
    if not is_hash_cryptographic(stored_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is not yet activated. Please use the account activation process."
        )
    
    if not DataRepository.check_otp_rate_limit(clean_roll, window_minutes=15, max_requests=3):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many reset requests. Please wait 15 minutes before requesting a new code."
        )
    
    registered_email = (student.get("email") or "").strip().lower()
    if not registered_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No verified contact details on record. Please visit the student affairs office."
        )
    
    otp = "".join(secrets.choice("0123456789") for _ in range(6))
    otp_hash = generate_otp_hash(otp, clean_roll, settings.SECRET_KEY)
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    
    DataRepository.save_otp(clean_roll, otp_hash, "PASSWORD_RESET", expires_at)
    
    subject = "VIGNAN-AI Password Reset Code"
    body = (
        f"Hello {student.get('full_name', 'Student')},\n\n"
        f"Your 6-digit password reset verification code is: {otp}\n\n"
        f"This code will expire in 10 minutes.\n"
        f"Vignan Foundation for Science, Technology and Research"
    )
    DataRepository.dispatch_student_email(registered_email, clean_roll, subject, body)
    
    masked = mask_email(registered_email)
    return RequestOtpResponse(
        success=True,
        message=f"A 6-digit password reset code has been dispatched to {masked}. Valid for 10 minutes.",
        masked_email=masked,
        expires_in_seconds=600,
        requires_admin_verification=False
    )


@router.post("/password-reset/verify-and-reset", response_model=AuthActionResponse)
async def verify_otp_and_reset_password(req: VerifyAndResetRequest):
    """
    Verifies OTP and resets password for an activated student.
    """
    clean_roll = req.roll_no.strip().upper()
    student = DataRepository.get_student_by_username(clean_roll)
    
    if not student or not clean_roll.startswith("251FA"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student registration number not found."
        )
    
    if req.new_password != req.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation password do not match."
        )
    
    validate_password_strength(req.new_password, clean_roll)
    
    otp_record = DataRepository.get_active_otp(clean_roll, "PASSWORD_RESET")
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending reset code found. Please request a new code."
        )
    
    try:
        exp_dt = datetime.fromisoformat(otp_record["expires_at"])
        if exp_dt.tzinfo is None:
            exp_dt = exp_dt.replace(tzinfo=timezone.utc)
    except Exception:
        exp_dt = datetime.now(timezone.utc) - timedelta(seconds=1)
        
    if datetime.now(timezone.utc) > exp_dt:
        DataRepository.mark_otp_used(otp_record["id"])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset code has expired. Please request a new code."
        )
    
    attempts_left = otp_record.get("attempts_left", 3)
    if attempts_left <= 0:
        DataRepository.mark_otp_used(otp_record["id"])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum verification attempts exceeded. Please request a new code."
        )
    
    is_valid = verify_otp_hash(req.otp, clean_roll, settings.SECRET_KEY, otp_record["otp_hash"])
    if not is_valid:
        new_attempts = attempts_left - 1
        is_used = 1 if new_attempts <= 0 else 0
        DataRepository.update_otp_attempts(otp_record["id"], new_attempts, is_used)
        if new_attempts <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum verification attempts exceeded. Please request a new code."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid verification code. Attempts remaining: {new_attempts}"
        )
    
    DataRepository.mark_otp_used(otp_record["id"])
    secure_hash = get_password_hash(req.new_password)
    DataRepository.update_student_password(clean_roll, secure_hash)
    
    return AuthActionResponse(
        success=True,
        message="Password reset successfully. You can now log in with your new password."
    )


@router.post("/login", response_model=Token)
async def login(req: LoginRequest):
    """
    Secure Student Authentication:
    - Verifies credentials against cryptographic hash (PBKDF2-SHA256 / bcrypt).
    - Strictly rejects unactivated accounts, universal backdoors, plaintext passwords, and roll-as-passwords.
    - Emits uniform error responses to prevent user-enumeration.
    """
    clean_username = req.username.strip().upper()
    student = DataRepository.get_student_by_username(clean_username)
    
    # Must be an approved institutional student
    if not student or not clean_username.startswith("251FA"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UNIFORM_AUTH_ERROR,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    stored_hash = student.get("password_hash") or ""
    
    # Strictly reject unactivated accounts
    if not is_hash_cryptographic(stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is not yet activated. Please activate your account first using your institutional registration number.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    is_valid = verify_password(req.password, stored_hash)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UNIFORM_AUTH_ERROR,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_payload = {
        "sub": student["user_id"],
        "student_id": student["student_id"],
        "roll_no": student["roll_no"],
        "full_name": student["full_name"],
        "programme_code": student["programme_code"],
        "role": "student"
    }
    
    token = create_access_token(token_payload)
    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=86400,
        student_id=student["student_id"],
        roll_no=student["roll_no"],
        full_name=student["full_name"],
        programme_code=student["programme_code"]
    )


@router.post("/activate", response_model=AuthActionResponse)
async def legacy_activate_account(req: AccountActivationRequest):
    """Legacy activation endpoint redirecting to OTP flow."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Please use the secure OTP-verified activation flow (/activation/request-otp and /activation/verify-and-activate)."
    )


@router.post("/reset-password", response_model=AuthActionResponse)
async def legacy_reset_password(req: PasswordResetRequest):
    """Legacy reset endpoint redirecting to OTP flow."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Please use the secure OTP-verified reset flow (/password-reset/request-otp and /password-reset/verify-and-reset)."
    )


@router.get("/me", response_model=StudentProfile)
async def get_my_profile(current_student: dict = Depends(get_current_student)):
    session = DatabaseSession(student_id=current_student["student_id"], user_id=current_student["user_id"])
    profile = DataRepository.get_student_profile(session)
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return StudentProfile(**profile)
