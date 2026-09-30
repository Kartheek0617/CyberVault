"""
CyberVault — Dashboard statistics API.
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import (
    AuditLog, Case, CaseStatus, Evidence,
    EvidenceStatus, IntegrityStatus,
    SecurityEvent, User, UserRole
)
from app.security.dependencies import get_current_active_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get dashboard statistics based on user role and accessible data."""
    # For admin/auditor: system-wide. For others: scoped.
    is_global = current_user.role in (UserRole.ADMIN, UserRole.AUDITOR)

    if is_global:
        active_cases = db.query(Case).filter(Case.status == CaseStatus.ACTIVE).count()
        closed_cases = db.query(Case).filter(Case.status == CaseStatus.CLOSED).count()
        total_evidence = db.query(Evidence).count()
        pending_transfers = db.query(Evidence).filter(Evidence.status == EvidenceStatus.TRANSFERRED).count()
        verified_evidence = db.query(Evidence).filter(Evidence.integrity_status == IntegrityStatus.VERIFIED).count()
        integrity_alerts = db.query(Evidence).filter(Evidence.integrity_status == IntegrityStatus.FAILED).count()
        total_users = db.query(User).count()
    else:
        from app.models.models import CaseMember
        my_case_ids = [
            c.id for c in db.query(Case).filter(Case.created_by_id == current_user.id).all()
        ] + [
            m.case_id for m in db.query(CaseMember).filter(CaseMember.user_id == current_user.id).all()
        ]
        my_case_ids = list(set(str(cid) for cid in my_case_ids))

        active_cases = db.query(Case).filter(
            Case.id.in_(my_case_ids), Case.status == CaseStatus.ACTIVE
        ).count()
        closed_cases = db.query(Case).filter(
            Case.id.in_(my_case_ids), Case.status == CaseStatus.CLOSED
        ).count()
        total_evidence = db.query(Evidence).filter(Evidence.case_id.in_(my_case_ids)).count()
        pending_transfers = db.query(Evidence).filter(
            Evidence.case_id.in_(my_case_ids), Evidence.status == EvidenceStatus.TRANSFERRED
        ).count()
        verified_evidence = db.query(Evidence).filter(
            Evidence.case_id.in_(my_case_ids), Evidence.integrity_status == IntegrityStatus.VERIFIED
        ).count()
        integrity_alerts = db.query(Evidence).filter(
            Evidence.case_id.in_(my_case_ids), Evidence.integrity_status == IntegrityStatus.FAILED
        ).count()
        total_users = None

    # Recent security events (last 24h)
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_security = db.query(SecurityEvent).filter(SecurityEvent.timestamp >= since).count()

    return {
        "active_cases": active_cases,
        "closed_cases": closed_cases,
        "total_evidence": total_evidence,
        "pending_transfers": pending_transfers,
        "verified_evidence": verified_evidence,
        "integrity_alerts": integrity_alerts,
        "total_users": total_users,
        "recent_security_events": recent_security,
    }


@router.get("/recent-activity")
async def get_recent_activity(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get recent audit log activity for the dashboard."""
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.sequence_number.desc())
        .limit(20)
        .all()
    )
    return {
        "activity": [
            {
                "id": str(log.id),
                "action": log.action.value,
                "resource_type": log.resource_type,
                "timestamp": log.timestamp.isoformat(),
                "is_security_event": log.is_security_event,
                "username": log.user.username if log.user else "system",
            }
            for log in logs
        ]
    }


@router.get("/security-events")
async def get_security_events(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get recent security events."""
    events = (
        db.query(SecurityEvent)
        .order_by(SecurityEvent.timestamp.desc())
        .limit(50)
        .all()
    )
    return {
        "events": [
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "severity": e.severity,
                "description": e.description,
                "timestamp": e.timestamp.isoformat(),
                "resolved": e.resolved,
            }
            for e in events
        ]
    }
