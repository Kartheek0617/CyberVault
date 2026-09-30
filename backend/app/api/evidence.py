"""
CyberVault — Evidence management API endpoints.
Security: IDOR protection, file validation, server-side authorization on every endpoint.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import (
    AuditAction, Case, ChainOfCustody, CustodyAction,
    Evidence, User, UserRole, EvidenceStatus
)
from app.schemas.schemas import (
    CustodyChainResponse, CustodyEventResponse,
    EvidenceIntegrityResult, EvidenceMetadataResponse,
    EvidenceTransferRequest, UserResponse
)
from app.security.dependencies import get_current_active_user, require_role
from app.services.audit_service import create_audit_log
from app.services.evidence_service import (
    check_case_access,
    receive_evidence,
    transfer_evidence,
    upload_evidence,
    verify_evidence_integrity,
)

router = APIRouter(prefix="/api", tags=["Evidence"])


def _check_evidence_access(db: Session, evidence: Evidence, user: User) -> bool:
    """
    IDOR/BOLA protection for evidence.
    User must have access to the parent case.
    Custodians can only access evidence they currently hold or are assigned to.
    """
    case = db.query(Case).filter(Case.id == evidence.case_id).first()
    if not case:
        return False

    if user.role in (UserRole.ADMIN, UserRole.AUDITOR):
        return True

    if not check_case_access(db, case, user):
        # For custodians: also check if they are the current custodian
        if user.role == UserRole.EVIDENCE_CUSTODIAN:
            return str(evidence.current_custodian_id) == str(user.id)
        return False
    return True


@router.post("/cases/{case_id}/evidence", status_code=status.HTTP_201_CREATED)
async def upload_evidence_endpoint(
    case_id: str,
    request: Request,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(require_role(
        UserRole.ADMIN, UserRole.INVESTIGATOR
    )),
    db: Session = Depends(get_db),
):
    """
    Secure evidence upload endpoint.
    Full validation pipeline: filename, extension, size, MIME, SHA-256, AES-256-GCM encryption.
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    if not check_case_access(db, case, current_user):
        create_audit_log(
            db=db,
            action=AuditAction.ACCESS_DENIED,
            user=current_user,
            resource_type="case",
            resource_id=case_id,
            details=f"Unauthorized evidence upload attempt by {current_user.username}",
            is_security_event=True,
        )
        raise HTTPException(status_code=403, detail="Access denied to this case.")

    file_bytes = await file.read()
    ip = request.client.host if request.client else None

    try:
        evidence = upload_evidence(
            db=db,
            case=case,
            uploader=current_user,
            filename=file.filename or "unknown",
            file_bytes=file_bytes,
            description=description,
            ip_address=ip,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": "Evidence uploaded and encrypted successfully.",
        "evidence_id": str(evidence.id),
        "evidence_number": evidence.evidence_number,
        "original_filename": evidence.original_filename,
        "sha256_hash": evidence.sha256_hash,
        "encryption_algorithm": evidence.encryption_algorithm,
        "file_size_bytes": evidence.file_size_bytes,
        "mime_type": evidence.mime_type,
    }


@router.get("/evidence/{evidence_id}", response_model=EvidenceMetadataResponse)
async def get_evidence_metadata(
    evidence_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get evidence metadata. IDOR-protected.
    NOTE: Does NOT return file contents (download requires separate endpoint).
    """
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found.")

    if not _check_evidence_access(db, evidence, current_user):
        create_audit_log(
            db=db,
            action=AuditAction.ACCESS_DENIED,
            user=current_user,
            resource_type="evidence",
            resource_id=evidence_id,
            details=f"Unauthorized evidence access attempt by {current_user.username}",
            is_security_event=True,
        )
        raise HTTPException(status_code=403, detail="Access denied.")

    create_audit_log(
        db=db,
        action=AuditAction.EVIDENCE_VIEWED,
        user=current_user,
        resource_type="evidence",
        resource_id=evidence_id,
    )

    return EvidenceMetadataResponse.model_validate(evidence)


@router.post("/evidence/{evidence_id}/verify")
async def verify_evidence(
    evidence_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Perform SHA-256 integrity verification on evidence.
    Decrypts, recomputes hash, compares with stored hash.
    """
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found.")

    if not _check_evidence_access(db, evidence, current_user):
        raise HTTPException(status_code=403, detail="Access denied.")

    ip = request.client.host if request.client else None

    try:
        result = verify_evidence_integrity(db=db, evidence=evidence, requestor=current_user, ip_address=ip)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail="Evidence file not found in secure storage.")

    return result


@router.post("/evidence/{evidence_id}/transfer")
async def transfer_evidence_endpoint(
    evidence_id: str,
    request: Request,
    body: EvidenceTransferRequest,
    current_user: User = Depends(require_role(
        UserRole.ADMIN, UserRole.INVESTIGATOR, UserRole.EVIDENCE_CUSTODIAN
    )),
    db: Session = Depends(get_db),
):
    """Transfer evidence custody to another user."""
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found.")

    if not _check_evidence_access(db, evidence, current_user):
        raise HTTPException(status_code=403, detail="Access denied.")

    # Only current custodian or admin can transfer
    if (
        current_user.role != UserRole.ADMIN
        and str(evidence.current_custodian_id) != str(current_user.id)
    ):
        raise HTTPException(status_code=403, detail="Only the current custodian can transfer evidence.")

    to_user = db.query(User).filter(User.id == body.to_user_id).first()
    if not to_user:
        raise HTTPException(status_code=404, detail="Target user not found.")

    if not to_user.is_active:
        raise HTTPException(status_code=400, detail="Target user is inactive.")

    ip = request.client.host if request.client else None
    custody = transfer_evidence(
        db=db,
        evidence=evidence,
        from_user=current_user,
        to_user=to_user,
        reason=body.reason,
        notes=body.notes,
        ip_address=ip,
    )

    return {
        "message": f"Evidence transferred to {to_user.username}.",
        "custody_event_id": str(custody.id),
        "event_hash": custody.event_hash,
    }


@router.post("/evidence/{evidence_id}/receive")
async def receive_evidence_endpoint(
    evidence_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Confirm receipt of transferred evidence."""
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found.")

    # Must be the current custodian
    if str(evidence.current_custodian_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="You are not the current custodian of this evidence.")

    ip = request.client.host if request.client else None
    custody = receive_evidence(db=db, evidence=evidence, receiver=current_user, ip_address=ip)

    return {
        "message": "Evidence receipt confirmed.",
        "custody_event_id": str(custody.id),
    }


@router.get("/evidence/{evidence_id}/custody", response_model=CustodyChainResponse)
async def get_custody_chain(
    evidence_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get the full chain-of-custody history for evidence."""
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found.")

    if not _check_evidence_access(db, evidence, current_user):
        raise HTTPException(status_code=403, detail="Access denied.")

    events = (
        db.query(ChainOfCustody)
        .filter(ChainOfCustody.evidence_id == evidence_id)
        .order_by(ChainOfCustody.timestamp.asc())
        .all()
    )

    return {
        "evidence_id": evidence.id,
        "evidence_number": evidence.evidence_number,
        "events": [CustodyEventResponse.model_validate(e) for e in events],
        "total_events": len(events),
    }


@router.get("/cases/{case_id}/evidence")
async def list_case_evidence(
    case_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all evidence for a case."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    if not check_case_access(db, case, current_user):
        raise HTTPException(status_code=403, detail="Access denied.")

    evidence_items = db.query(Evidence).filter(Evidence.case_id == case_id).order_by(Evidence.created_at.desc()).all()

    result = []
    for e in evidence_items:
        item = EvidenceMetadataResponse.model_validate(e).model_dump()
        if e.uploaded_by:
            item["uploaded_by"] = UserResponse.model_validate(e.uploaded_by).model_dump()
        if e.current_custodian:
            item["current_custodian"] = UserResponse.model_validate(e.current_custodian).model_dump()
        result.append(item)

    return {"evidence": result, "total": len(result)}
