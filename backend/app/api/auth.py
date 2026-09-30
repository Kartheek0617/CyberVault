"""
CyberVault — Authentication API endpoints.
Security:
  - Rate limiting on login endpoint
  - Argon2id password verification
  - Generic error messages (no username enumeration)
  - Account status checking
  - Failed login tracking
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AuditAction, SecurityEvent, User, UserRole
from app.schemas.schemas import LoginRequest, TokenResponse, UserResponse
from app.security.dependencies import get_current_active_user
from app.security.jwt import create_access_token
from app.security.password import hash_password, validate_password_strength, verify_password
from app.services.audit_service import create_audit_log
from app.core.config import get_settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
settings = get_settings()

# ── Simple in-memory rate limiter ──────────────────────────────────────────
# In production, use Redis-backed slowapi or similar
_login_attempts: dict[str, list[datetime]] = {}


def _check_rate_limit(ip: str) -> bool:
    """Returns True if the request should be blocked (rate limited)."""
    now = datetime.now(timezone.utc)
    window = settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS
    max_attempts = settings.LOGIN_RATE_LIMIT_MAX

    attempts = _login_attempts.get(ip, [])
    # Remove expired attempts
    attempts = [t for t in attempts if (now - t).total_seconds() < window]
    _login_attempts[ip] = attempts

    if len(attempts) >= max_attempts:
        return True
    return False


def _record_attempt(ip: str):
    now = datetime.now(timezone.utc)
    _login_attempts.setdefault(ip, []).append(now)


def _clear_attempts(ip: str):
    _login_attempts.pop(ip, None)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    body: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return a JWT access token.
    Rate limited. Generic error messages to prevent enumeration.
    """
    client_ip = request.client.host if request.client else "unknown"

    # Rate limit check
    if _check_rate_limit(client_ip):
        # Log security event
        db.add(SecurityEvent(
            event_type="LOGIN_RATE_LIMITED",
            severity="WARNING",
            source_ip=client_ip,
            description=f"Login rate limit exceeded from {client_ip}",
        ))
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )

    # Generic error to prevent username enumeration
    INVALID_CRED_MSG = "Invalid username or password."

    user: Optional[User] = db.query(User).filter(User.username == body.username).first()

    if not user:
        _record_attempt(client_ip)
        create_audit_log(
            db=db,
            action=AuditAction.USER_LOGIN_FAILED,
            resource_type="auth",
            details=f"Failed login attempt for username '{body.username}' from {client_ip}",
            ip_address=client_ip,
            is_security_event=True,
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CRED_MSG)

    if not user.is_active:
        _record_attempt(client_ip)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled.")

    if not verify_password(body.password, user.password_hash):
        _record_attempt(client_ip)
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        db.add(user)
        db.commit()
        create_audit_log(
            db=db,
            action=AuditAction.USER_LOGIN_FAILED,
            user=user,
            resource_type="auth",
            details=f"Invalid password attempt for user {user.username} from {client_ip}",
            ip_address=client_ip,
            is_security_event=True,
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CRED_MSG)

    # Successful login
    _clear_attempts(client_ip)
    user.failed_login_attempts = 0
    user.last_login = datetime.now(timezone.utc)
    db.add(user)
    db.commit()

    token = create_access_token(subject=str(user.id), role=user.role.value)

    create_audit_log(
        db=db,
        action=AuditAction.USER_LOGIN,
        user=user,
        resource_type="auth",
        details=f"Successful login from {client_ip}",
        ip_address=client_ip,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
        username=user.username,
        role=user.role.value,
        full_name=user.full_name,
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Logout endpoint.
    Since JWT is stateless, this primarily records the audit event.
    Frontend should discard the token.
    """
    client_ip = request.client.host if request.client else "unknown"
    create_audit_log(
        db=db,
        action=AuditAction.USER_LOGOUT,
        user=current_user,
        resource_type="auth",
        details=f"User {current_user.username} logged out from {client_ip}",
        ip_address=client_ip,
    )
    return {"message": "Logged out successfully."}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Return the currently authenticated user's profile (no secrets)."""
    return current_user


@router.post("/reset-rate-limit")
async def reset_rate_limit(request: Request):
    """
    Demo/Classroom safe reset mechanism.
    Clears the in-memory IP rate limit cache ONLY if DEBUG mode is enabled.
    In production (DEBUG=False), this endpoint safely does nothing or warns.
    """
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rate limit reset is disabled in production environments."
        )
    
    client_ip = request.client.host if request.client else "unknown"
    
    # Restrict reset mechanism to localhost (or test environments)
    if client_ip not in ("127.0.0.1", "::1", "testclient"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reset mechanism is restricted to localhost in development."
        )

    if client_ip in _login_attempts:
        _clear_attempts(client_ip)
        return {"message": f"Rate limit cleared for IP: {client_ip}"}
    
    return {"message": "No rate limit state found for this IP."}
