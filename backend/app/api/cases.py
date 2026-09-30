"""
CyberVault — Case management API endpoints.
Security: IDOR/BOLA protection — every request checks if the user can access the case.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import (
    AuditAction, Case, CaseMember, CaseStatus, Evidence, User, UserRole
)
from app.schemas.schemas import (
    CaseMemberAdd, CaseCreate, CaseDetailResponse,
    CaseResponse, UserResponse
)
from app.security.dependencies import get_current_active_user, require_role
from app.services.audit_service import create_audit_log
from app.services.evidence_service import check_case_access
from datetime import datetime, timezone

router = APIRouter(prefix="/api/cases", tags=["Cases"])


def _generate_case_number(db: Session) -> str:
    count = db.query(Case).count()
    year = datetime.now(timezone.utc).year
    return f"CASE-{year}-{(count + 1):03d}"


@router.get("")
async def list_cases(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = None,
):
    """
    List cases accessible to the current user.
    IDOR protection: non-admin/auditor users only see cases they're members of.
    """
    query = db.query(Case)

    if current_user.role not in (UserRole.ADMIN, UserRole.AUDITOR):
        # Filter to cases where user is creator or member
        member_case_ids = [
            m.case_id for m in db.query(CaseMember.case_id)
            .filter(CaseMember.user_id == current_user.id).all()
        ]
        created_case_ids = [
            c.id for c in db.query(Case.id)
            .filter(Case.created_by_id == current_user.id).all()
        ]
        accessible_ids = list(set([str(cid) for cid in member_case_ids + created_case_ids]))
        query = query.filter(Case.id.in_(accessible_ids))

    if status_filter:
        try:
            status_enum = CaseStatus(status_filter.upper())
            query = query.filter(Case.status == status_enum)
        except ValueError:
            pass

    cases = query.order_by(Case.created_at.desc()).all()

    result = []
    for case in cases:
        evidence_count = db.query(Evidence).filter(Evidence.case_id == case.id).count()
        member_count = db.query(CaseMember).filter(CaseMember.case_id == case.id).count()
        d = CaseResponse.model_validate(case).model_dump()
        d["evidence_count"] = evidence_count
        d["member_count"] = member_count
        d["creator"] = UserResponse.model_validate(case.creator).model_dump() if case.creator else None
        result.append(d)

    return {"cases": result, "total": len(result)}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_case(
    request: Request,
    body: CaseCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INVESTIGATOR)),
    db: Session = Depends(get_db),
):
    """Create a new investigation case."""
    case_number = _generate_case_number(db)

    case = Case(
        case_number=case_number,
        title=body.title,
        description=body.description,
        case_type=body.case_type,
        priority=body.priority,
        status=CaseStatus.ACTIVE,
        created_by_id=current_user.id,
    )
    db.add(case)
    db.flush()

    # Add creator as a member
    membership = CaseMember(
        case_id=case.id,
        user_id=current_user.id,
        role_in_case="LEAD_INVESTIGATOR",
    )
    db.add(membership)
    db.commit()
    db.refresh(case)

    create_audit_log(
        db=db,
        action=AuditAction.CASE_CREATED,
        user=current_user,
        resource_type="case",
        resource_id=str(case.id),
        details=f"Case {case_number} created: {body.title}",
        ip_address=request.client.host if request.client else None,
    )

    return CaseResponse.model_validate(case)


@router.get("/{case_id}")
async def get_case(
    case_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get case details. IDOR-protected: checks authorization before returning data."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        # Return 404 (not 403) to avoid leaking case existence to unauthorized users
        raise HTTPException(status_code=404, detail="Case not found.")

    if not check_case_access(db, case, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    create_audit_log(
        db=db,
        action=AuditAction.CASE_VIEWED,
        user=current_user,
        resource_type="case",
        resource_id=str(case.id),
        details=f"Case {case.case_number} viewed by {current_user.username}",
    )

    members = [
        UserResponse.model_validate(m.user).model_dump()
        for m in case.members if m.user
    ]
    evidence_items = db.query(Evidence).filter(Evidence.case_id == case.id).all()
    evidence_summary = [
        {
            "id": str(e.id),
            "evidence_number": e.evidence_number,
            "original_filename": e.original_filename,
            "sha256_hash": e.sha256_hash,
            "integrity_status": e.integrity_status.value,
            "status": e.status.value,
            "created_at": e.created_at.isoformat(),
        }
        for e in evidence_items
    ]

    data = CaseResponse.model_validate(case).model_dump()
    data["members"] = members
    data["evidence_summary"] = evidence_summary
    data["creator"] = UserResponse.model_validate(case.creator).model_dump() if case.creator else None
    return data


@router.put("/{case_id}")
async def update_case(
    case_id: str,
    request: Request,
    body: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update case details. Only creator or admin can update."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    if not check_case_access(db, case, current_user):
        raise HTTPException(status_code=403, detail="Access denied.")

    if current_user.role not in (UserRole.ADMIN,) and str(case.created_by_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Only the case creator or admin can update this case.")

    allowed_fields = {"title", "description", "priority", "status"}
    for field, value in body.items():
        if field in allowed_fields and value is not None:
            setattr(case, field, value)

    if "status" in body and body["status"] == "CLOSED":
        case.closed_at = datetime.now(timezone.utc)

    db.add(case)
    db.commit()
    db.refresh(case)

    create_audit_log(
        db=db,
        action=AuditAction.CASE_UPDATED,
        user=current_user,
        resource_type="case",
        resource_id=str(case.id),
        details=f"Case {case.case_number} updated by {current_user.username}",
        ip_address=request.client.host if request.client else None,
    )

    return CaseResponse.model_validate(case)


@router.post("/{case_id}/members")
async def add_case_member(
    case_id: str,
    request: Request,
    body: CaseMemberAdd,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INVESTIGATOR)),
    db: Session = Depends(get_db),
):
    """Add a member to a case."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    if not check_case_access(db, case, current_user):
        raise HTTPException(status_code=403, detail="Access denied.")

    target_user = db.query(User).filter(User.id == body.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")

    existing = db.query(CaseMember).filter(
        CaseMember.case_id == case.id, CaseMember.user_id == body.user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member of this case.")

    membership = CaseMember(
        case_id=case.id,
        user_id=body.user_id,
        role_in_case=body.role_in_case,
    )
    db.add(membership)
    db.commit()

    return {"message": f"User {target_user.username} added to case {case.case_number}."}
