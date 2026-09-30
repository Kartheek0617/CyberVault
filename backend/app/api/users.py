"""
CyberVault — User management API (Admin only).
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AuditAction, User, UserRole
from app.schemas.schemas import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.security.dependencies import get_current_active_user, require_role
from app.security.password import hash_password, validate_password_strength
from app.services.audit_service import create_audit_log

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("", response_model=UserListResponse)
async def list_users(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
):
    """List all users. Admin and Auditor only."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return UserListResponse(users=users, total=len(users))


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    body: UserCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Create a new user. Admin only."""
    # Check uniqueness
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="Username already exists.")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")

    valid, err = validate_password_strength(body.password)
    if not valid:
        raise HTTPException(status_code=400, detail=err)

    user = User(
        username=body.username,
        email=str(body.email),
        full_name=body.full_name,
        password_hash=hash_password(body.password),
        role=body.role,
        badge_number=body.badge_number,
        department=body.department,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    create_audit_log(
        db=db,
        action=AuditAction.USER_CREATED,
        user=current_user,
        resource_type="user",
        resource_id=str(user.id),
        details=f"User {user.username} created with role {user.role.value}",
        ip_address=request.client.host if request.client else None,
    )

    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: Request,
    body: UserUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Update user details. Admin only."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if body.full_name is not None:
        user.full_name = body.full_name
    if body.email is not None:
        user.email = str(body.email)
    if body.role is not None:
        user.role = body.role
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.badge_number is not None:
        user.badge_number = body.badge_number
    if body.department is not None:
        user.department = body.department

    db.add(user)
    db.commit()
    db.refresh(user)

    create_audit_log(
        db=db,
        action=AuditAction.USER_UPDATED,
        user=current_user,
        resource_type="user",
        resource_id=str(user.id),
        details=f"User {user.username} updated by {current_user.username}",
        ip_address=request.client.host if request.client else None,
    )

    return user
