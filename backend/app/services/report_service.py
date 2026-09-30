"""
CyberVault — Report generation and digital signature service.
Implements Ed25519-signed evidence reports with PDF generation.
"""
import hashlib
import json
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.models import (
    AuditAction, Case, ChainOfCustody, DigitalSignature,
    Evidence, Report, User
)
from app.security.signatures import get_public_key_hex, sign_data, verify_signature
from app.services.audit_service import create_audit_log


def _generate_report_number(db: Session) -> str:
    count = db.query(Report).count()
    year = datetime.now(timezone.utc).year
    return f"RPT-{year}-{(count + 1):04d}"


def _build_report_content(
    db: Session,
    case: Case,
    evidence_items: List[Evidence],
    generated_by: User,
) -> dict:
    """Build the structured report content dictionary."""
    custody_summaries = []
    for ev in evidence_items:
        events = (
            db.query(ChainOfCustody)
            .filter(ChainOfCustody.evidence_id == ev.id)
            .order_by(ChainOfCustody.timestamp.asc())
            .all()
        )
        custody_summaries.append({
            "evidence_id": str(ev.id),
            "evidence_number": ev.evidence_number,
            "original_filename": ev.original_filename,
            "sha256_hash": ev.sha256_hash,
            "integrity_status": ev.integrity_status.value,
            "encryption_algorithm": ev.encryption_algorithm,
            "file_size_bytes": ev.file_size_bytes,
            "mime_type": ev.mime_type,
            "events": [
                {
                    "action": e.action.value,
                    "timestamp": e.timestamp.isoformat(),
                    "event_hash": e.event_hash,
                }
                for e in events
            ],
        })

    return {
        "report_metadata": {
            "system": "CyberVault — Secure Digital Evidence Management System",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": {
                "id": str(generated_by.id),
                "username": generated_by.username,
                "full_name": generated_by.full_name,
                "role": generated_by.role.value,
                "badge_number": generated_by.badge_number,
            },
        },
        "case": {
            "id": str(case.id),
            "case_number": case.case_number,
            "title": case.title,
            "description": case.description,
            "type": case.case_type.value,
            "priority": case.priority.value,
            "status": case.status.value,
            "created_at": case.created_at.isoformat(),
        },
        "evidence_items": custody_summaries,
        "evidence_count": len(evidence_items),
        "security_summary": {
            "encryption": "AES-256-GCM",
            "hash_algorithm": "SHA-256",
            "signature_algorithm": "Ed25519",
            "custody_hash_chain": "SHA-256 linked list",
        },
    }


def generate_report(
    db: Session,
    case: Case,
    evidence_ids: List[UUID],
    generated_by: User,
    title: str,
    ip_address: str = None,
) -> Report:
    """
    Generate a digitally signed evidence report.
    Steps:
    1. Collect evidence metadata
    2. Build report content
    3. Serialize to canonical JSON
    4. Calculate SHA-256 of report
    5. Sign with Ed25519 private key
    6. Store report and signature
    """
    # Fetch and authorize evidence
    evidence_items = []
    for eid in evidence_ids:
        ev = db.query(Evidence).filter(
            Evidence.id == eid,
            Evidence.case_id == case.id,
        ).first()
        if ev:
            evidence_items.append(ev)

    if not evidence_items:
        raise ValueError("No valid evidence items found for this case.")

    # Build report content
    content = _build_report_content(db, case, evidence_items, generated_by)
    content_json = json.dumps(content, sort_keys=True, default=str)
    content_bytes = content_json.encode("utf-8")

    # SHA-256 of report content
    report_hash = hashlib.sha256(content_bytes).hexdigest()

    # Ed25519 signature
    signature_hex, public_key_hex, signed_data_hash = sign_data(content_bytes)

    report_number = _generate_report_number(db)

    report = Report(
        report_number=report_number,
        case_id=case.id,
        generated_by_id=generated_by.id,
        title=title,
        evidence_ids=json.dumps([str(eid) for eid in evidence_ids]),
        report_hash=report_hash,
        digital_signature=signature_hex,
        signature_algorithm="Ed25519",
        is_signed=True,
        report_content=content_json,
    )
    db.add(report)
    db.flush()

    # Store signature details for non-repudiation
    sig_record = DigitalSignature(
        report_id=report.id,
        signer_id=generated_by.id,
        algorithm="Ed25519",
        signature_hex=signature_hex,
        public_key_hex=public_key_hex,
        signed_data_hash=signed_data_hash,
        is_valid=True,
        last_verified_at=datetime.now(timezone.utc),
    )
    db.add(sig_record)
    db.commit()
    db.refresh(report)

    create_audit_log(
        db=db,
        action=AuditAction.REPORT_GENERATED,
        user=generated_by,
        resource_type="report",
        resource_id=str(report.id),
        details=f"Report {report_number} generated for case {case.case_number}. Hash: {report_hash}",
        ip_address=ip_address,
    )

    create_audit_log(
        db=db,
        action=AuditAction.REPORT_SIGNED,
        user=generated_by,
        resource_type="report",
        resource_id=str(report.id),
        details=f"Report {report_number} digitally signed with Ed25519.",
        ip_address=ip_address,
    )

    return report


def verify_report_signature(
    db: Session,
    report: Report,
    verifier: User,
    ip_address: str = None,
) -> dict:
    """
    Verify the digital signature of a report.
    Uses the public key stored at signing time (archived for non-repudiation).
    """
    sig_record = db.query(DigitalSignature).filter(
        DigitalSignature.report_id == report.id
    ).first()

    if not sig_record:
        return {
            "report_id": report.id,
            "report_number": report.report_number,
            "is_valid": False,
            "status": "INVALID — No signature record found.",
            "signed_at": None,
            "signer": None,
            "algorithm": "Ed25519",
            "verified_at": datetime.now(timezone.utc),
        }

    # Re-compute report content bytes for verification
    content_bytes = report.report_content.encode("utf-8") if report.report_content else b""

    is_valid = verify_signature(
        data=content_bytes,
        signature_hex=sig_record.signature_hex,
        public_key_hex=sig_record.public_key_hex,
    )

    # Update signature record
    sig_record.is_valid = is_valid
    sig_record.last_verified_at = datetime.now(timezone.utc)
    db.add(sig_record)
    db.commit()

    signer = db.query(User).filter(User.id == sig_record.signer_id).first()

    create_audit_log(
        db=db,
        action=AuditAction.SIGNATURE_VERIFIED,
        user=verifier,
        resource_type="report",
        resource_id=str(report.id),
        details=f"Signature verification for report {report.report_number}: {'VALID' if is_valid else 'INVALID'}",
        ip_address=ip_address,
        is_security_event=not is_valid,
    )

    return {
        "report_id": report.id,
        "report_number": report.report_number,
        "is_valid": is_valid,
        "status": "VALID SIGNATURE — Report integrity confirmed." if is_valid else "INVALID SIGNATURE — Report may have been tampered with.",
        "signed_at": sig_record.signed_at,
        "signer": signer.username if signer else None,
        "algorithm": sig_record.algorithm,
        "verified_at": datetime.now(timezone.utc),
    }
