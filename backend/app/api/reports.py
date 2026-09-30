"""
CyberVault — Report generation and digital signature API endpoints.
"""
import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Case, Report, User, UserRole
from app.schemas.schemas import ReportCreate, SignatureVerificationResult
from app.security.dependencies import get_current_active_user, require_role
from app.services.evidence_service import check_case_access
from app.services.report_service import generate_report, verify_report_signature

router = APIRouter(prefix="/api", tags=["Reports"])


@router.post("/cases/{case_id}/reports", status_code=status.HTTP_201_CREATED)
async def create_report(
    case_id: str,
    request: Request,
    body: ReportCreate,
    current_user: User = Depends(require_role(
        UserRole.ADMIN, UserRole.INVESTIGATOR, UserRole.AUDITOR
    )),
    db: Session = Depends(get_db),
):
    """Generate and digitally sign an evidence report for a case."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    if not check_case_access(db, case, current_user):
        raise HTTPException(status_code=403, detail="Access denied.")

    ip = request.client.host if request.client else None

    try:
        report = generate_report(
            db=db,
            case=case,
            evidence_ids=body.evidence_ids,
            generated_by=current_user,
            title=body.title,
            ip_address=ip,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": "Report generated and digitally signed.",
        "report_id": str(report.id),
        "report_number": report.report_number,
        "report_hash": report.report_hash,
        "is_signed": report.is_signed,
        "signature_algorithm": report.signature_algorithm,
    }


@router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a report by ID with full content."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    case = db.query(Case).filter(Case.id == report.case_id).first()
    if not case or not check_case_access(db, case, current_user):
        raise HTTPException(status_code=403, detail="Access denied.")

    content = json.loads(report.report_content) if report.report_content else None

    return {
        "id": str(report.id),
        "report_number": report.report_number,
        "case_id": str(report.case_id),
        "title": report.title,
        "report_hash": report.report_hash,
        "digital_signature": report.digital_signature,
        "signature_algorithm": report.signature_algorithm,
        "is_signed": report.is_signed,
        "created_at": report.created_at.isoformat(),
        "generated_by": {
            "id": str(report.generated_by_user.id),
            "username": report.generated_by_user.username,
            "full_name": report.generated_by_user.full_name,
        } if report.generated_by_user else None,
        "report_content": content,
    }


@router.post("/reports/{report_id}/verify-signature", response_model=SignatureVerificationResult)
async def verify_signature_endpoint(
    report_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Verify the Ed25519 digital signature of a report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    case = db.query(Case).filter(Case.id == report.case_id).first()
    if not case or not check_case_access(db, case, current_user):
        raise HTTPException(status_code=403, detail="Access denied.")

    ip = request.client.host if request.client else None
    result = verify_report_signature(db=db, report=report, verifier=current_user, ip_address=ip)

    return SignatureVerificationResult(**result)


@router.get("/cases/{case_id}/reports")
async def list_case_reports(
    case_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all reports for a case."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    if not check_case_access(db, case, current_user):
        raise HTTPException(status_code=403, detail="Access denied.")

    reports = db.query(Report).filter(Report.case_id == case_id).order_by(Report.created_at.desc()).all()

    return {
        "reports": [
            {
                "id": str(r.id),
                "report_number": r.report_number,
                "title": r.title,
                "report_hash": r.report_hash,
                "is_signed": r.is_signed,
                "created_at": r.created_at.isoformat(),
            }
            for r in reports
        ],
        "total": len(reports),
    }
