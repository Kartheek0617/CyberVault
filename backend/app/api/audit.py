"""
CyberVault — Audit log API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AuditAction, AuditLog, User, UserRole
from app.schemas.schemas import AuditIntegrityResult, AuditLogResponse
from app.security.dependencies import get_current_active_user, require_role
from app.services.audit_service import create_audit_log, verify_audit_log_integrity

router = APIRouter(prefix="/api/audit", tags=["Audit"])


@router.get("")
async def get_audit_logs(
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
    is_security: bool = False,
):
    """Get paginated audit logs. Admin and Auditor only."""
    query = db.query(AuditLog)
    if is_security:
        query = query.filter(AuditLog.is_security_event == True)
    total = query.count()
    logs = query.order_by(AuditLog.sequence_number.desc()).offset(offset).limit(limit).all()

    return {
        "audit_logs": [AuditLogResponse.model_validate(log) for log in logs],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.post("/verify", response_model=AuditIntegrityResult)
async def verify_audit_integrity(
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
):
    """
    Verify the integrity of the entire audit log hash chain.
    Returns 'AUDIT LOG INTEGRITY VERIFIED' or 'AUDIT LOG TAMPERING DETECTED'.
    """
    result = verify_audit_log_integrity(db)

    create_audit_log(
        db=db,
        action=AuditAction.AUDIT_VERIFIED,
        user=current_user,
        resource_type="audit_log",
        details=f"Audit log integrity verification: {'PASSED' if result['is_valid'] else 'FAILED'}",
        ip_address=request.client.host if request.client else None,
        is_security_event=not result["is_valid"],
    )

    return AuditIntegrityResult(**result)
