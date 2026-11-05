import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import json
import base64

# Robust JWT handling with native HMAC-SHA256 fallback
try:
    from jose import JWTError, jwt
except ImportError:
    class JWTError(Exception):
        """Fallback JWT decoding / validation error."""
        pass

    class _NativeJWT:
        @staticmethod
        def _b64encode(data: bytes) -> str:
            return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

        @staticmethod
        def _b64decode(data: str) -> bytes:
            padding = 4 - (len(data) % 4)
            if padding != 4:
                data += "=" * padding
            return base64.urlsafe_b64decode(data)

        @classmethod
        def encode(cls, claims: dict, key: str, algorithm: str = "HS256") -> str:
            header = {"alg": "HS256", "typ": "JWT"}
            hdr_b64 = cls._b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
            pay_b64 = cls._b64encode(json.dumps(claims, default=str, separators=(",", ":")).encode("utf-8"))
            msg = f"{hdr_b64}.{pay_b64}".encode("utf-8")
            sig = hmac.new(key.encode("utf-8"), msg, hashlib.sha256).digest()
            sig_b64 = cls._b64encode(sig)
            return f"{hdr_b64}.{pay_b64}.{sig_b64}"

        @classmethod
        def decode(cls, token: str, key: str, algorithms: Optional[list] = None) -> dict:
            try:
                parts = token.split(".")
                if len(parts) != 3:
                    raise JWTError("Invalid token format")
                hdr_b64, pay_b64, sig_b64 = parts
                msg = f"{hdr_b64}.{pay_b64}".encode("utf-8")
                expected_sig = hmac.new(key.encode("utf-8"), msg, hashlib.sha256).digest()
                actual_sig = cls._b64decode(sig_b64)
                if not hmac.compare_digest(expected_sig, actual_sig):
                    raise JWTError("Signature verification failed")
                payload = json.loads(cls._b64decode(pay_b64).decode("utf-8"))
                exp = payload.get("exp")
                if exp:
                    now_ts = datetime.now(timezone.utc).timestamp()
                    if isinstance(exp, (int, float)) and now_ts > exp:
                        raise JWTError("Token has expired")
                return payload
            except Exception as e:
                raise JWTError(str(e)) from e

    jwt = _NativeJWT()

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

# Password hasher context (bcrypt primary with PBKDF2 fallback)
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")
except Exception:
    pwd_context = None

# Bearer security scheme
security_scheme = HTTPBearer(auto_error=True)


def get_password_hash(password: str) -> str:
    """
    Generates a secure cryptographic password hash.
    Uses passlib/bcrypt if available; otherwise uses OWASP-recommended PBKDF2-HMAC-SHA256
    with 100,000 iterations and a 16-byte cryptographically secure random salt.
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    if pwd_context is not None:
        try:
            return pwd_context.hash(password)
        except Exception:
            pass
    
    # Standard library secure PBKDF2-HMAC-SHA256 fallback
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"pbkdf2_sha256$100000${salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Cryptographically verifies a plaintext password against a stored secure hash.
    STRICT SECURITY CONTROLS:
    - Never accepts plaintext matches or registration numbers as passwords.
    - Never accepts universal backdoor strings (e.g. 'student123').
    - Never accepts mock prefixes.
    - Uses constant-time digest comparison to prevent timing side-channel attacks.
    """
    if not plain_password or not hashed_password:
        return False

    # Verify standard PBKDF2 format: pbkdf2_sha256$iterations$salt$hash
    if hashed_password.startswith("pbkdf2_sha256$"):
        try:
            parts = hashed_password.split("$")
            if len(parts) == 4:
                iterations = int(parts[1])
                salt = parts[2]
                expected_hash_hex = parts[3]
                computed = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), iterations)
                return hmac.compare_digest(computed.hex(), expected_hash_hex)
        except Exception:
            return False

    # Verify bcrypt hashes ($2b$, $2a$, $2y$)
    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        if pwd_context is not None:
            try:
                return pwd_context.verify(plain_password, hashed_password)
            except Exception:
                return False

    return False


def is_hash_cryptographic(hash_val: Optional[str]) -> bool:
    """Returns True if hash_val is a recognized salted cryptographic hash."""
    if not hash_val:
        return False
    h = hash_val.strip()
    return h.startswith("pbkdf2_sha256$") or h.startswith(("$2a$", "$2b$", "$2y$"))


def mask_email(email: Optional[str]) -> str:
    """Masks email for privacy-safe display: 251fa04e13@vignan.ac.in -> 25***13@vignan.ac.in."""
    if not email or "@" not in email:
        return "***@vignan.ac.in"
    local_part, domain = email.split("@", 1)
    if len(local_part) <= 4:
        masked_local = local_part[0] + "***" + local_part[-1] if len(local_part) > 1 else "***"
    else:
        masked_local = local_part[:2] + "***" + local_part[-2:]
    return f"{masked_local}@{domain}"


def generate_otp_hash(otp: str, roll_no: str, secret_key: str) -> str:
    """Generates salted SHA-256 hash of OTP."""
    msg = f"{otp.strip()}:{secret_key}:{roll_no.strip().upper()}".encode("utf-8")
    return hashlib.sha256(msg).hexdigest()


def verify_otp_hash(otp: str, roll_no: str, secret_key: str, expected_hash: str) -> bool:
    """Constant-time comparison of OTP against expected hash."""
    if not otp or not expected_hash:
        return False
    computed = generate_otp_hash(otp, roll_no, secret_key)
    return hmac.compare_digest(computed, expected_hash)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_student(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate student credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        student_id: str = payload.get("student_id")
        roll_no: str = payload.get("roll_no")
        full_name: str = payload.get("full_name")
        if user_id is None or student_id is None:
            raise credentials_exception
        return {
            "user_id": user_id,
            "student_id": student_id,
            "roll_no": roll_no,
            "full_name": full_name or "Student"
        }
    except JWTError:
        raise credentials_exception


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> Dict[str, Any]:
    """
    Verifies that the caller has a valid administrative JWT bearer token.
    Prevents unauthorized inspection or deletion of student tickets and system settings.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Administrative authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        admin_id: str = payload.get("admin_id") or payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)
        role: str = payload.get("role", "")
        
        # Check administrative role privileges
        if not admin_id or (not is_admin and role.lower() not in ("admin", "chief nodal officer", "nodal officer")):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Administrative privileges required",
            )
        return {
            "admin_id": admin_id,
            "username": payload.get("username", "admin"),
            "name": payload.get("name", "Nodal Officer"),
            "role": role or "Admin"
        }
    except JWTError:
        raise credentials_exception


def verify_student_access(current_student: Dict[str, Any], requested_student_id: str) -> None:
    """
    Row-Level Security Guardrail:
    Ensures an authenticated student can only access their own records,
    preventing IDOR (Insecure Direct Object Reference) vulnerabilities.
    """
    if not requested_student_id:
        return
    req_clean = requested_student_id.strip().upper()
    curr_id = (current_student.get("student_id") or "").strip().upper()
    curr_roll = (current_student.get("roll_no") or "").strip().upper()

    if req_clean != curr_id and req_clean != curr_roll:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You are only authorized to access your own student record."
        )
