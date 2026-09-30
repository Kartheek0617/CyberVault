"""
CyberVault — Evidence service.
Handles secure upload, storage, retrieval, and integrity verification.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.models import (
    AuditAction, Case, CaseMember, ChainOfCustody,
    CustodyAction, Evidence, EvidenceStatus, IntegrityStatus, User, UserRole
)
from app.schemas.schemas import EvidenceTransferRequest
from app.security.encryption import (
    calculate_sha256,
    decrypt_evidence,
    encrypt_evidence,
    generate_event_hash,
    generate_storage_filename,
)
from app.security.file_validator import (
    detect_mime_type,
    validate_extension,
    validate_file_size,
    validate_filename,
    validate_mime_against_extension,
)
from app.services.audit_service import create_audit_log

settings = get_settings()


def _generate_evidence_number(db: Session) -> str:
    """Generate a sequential evidence number."""
    count = db.query(Evidence).count()
    year = datetime.now(timezone.utc).year
    return f"EV-{year}-{(count + 1):04d}"


def _generate_custody_event_hash(
    db: Session,
    evidence_id: UUID,
    action: CustodyAction,
    actor_id: UUID,
    timestamp: datetime,
) -> tuple[str, str]:
    """Calculate hash chain for custody events."""
    last = (
        db.query(ChainOfCustody)
        .filter(ChainOfCustody.evidence_id == evidence_id)
        .order_by(ChainOfCustody.timestamp.desc())
        .first()
    )
    prev_hash = last.event_hash if last else None
    event_data = json.dumps({
        "evidence_id": str(evidence_id),
        "action": action.value,
        "actor_id": str(actor_id),
        "timestamp": timestamp.isoformat(),
    }, sort_keys=True)
    current_hash = generate_event_hash(prev_hash, event_data)
    return prev_hash, current_hash


def check_case_access(db: Session, case: Case, user: User) -> bool:
    """
    IDOR/BOLA protection: verify the user is authorized to access this case.
    Admins and Auditors have broad access. Others must be case members or creators.
    """
    if user.role in (UserRole.ADMIN, UserRole.AUDITOR):
        return True
    if str(case.created_by_id) == str(user.id):
        return True
    membership = (
        db.query(CaseMember)
        .filter(CaseMember.case_id == case.id, CaseMember.user_id == user.id)
        .first()
    )
    return membership is not None


def upload_evidence(
    db: Session,
    case: Case,
    uploader: User,
    filename: str,
    file_bytes: bytes,
    description: Optional[str],
    ip_address: Optional[str],
) -> Evidence:
    """
    Secure evidence upload pipeline:
    1. Validate filename (path traversal prevention)
    2. Validate extension
    3. Validate file size
    4. Detect and validate MIME type
    5. Calculate SHA-256 of original file
    6. Encrypt with AES-256-GCM
    7. Write encrypted file with random storage name
    8. Store metadata in DB
    9. Create custody event
    10. Create audit log
    """
    # ── 1. Filename validation ─────────────────────────────────────────────
    valid, err = validate_filename(filename)
    if not valid:
        raise ValueError(f"Invalid filename: {err}")

    # ── 2. Extension validation ────────────────────────────────────────────
    valid, err, ext = validate_extension(filename)
    if not valid:
        raise ValueError(f"Forbidden file type: {err}")

    # ── 3. File size validation ────────────────────────────────────────────
    valid, err = validate_file_size(len(file_bytes))
    if not valid:
        raise ValueError(f"File size error: {err}")

    # ── 4. MIME type detection and validation ──────────────────────────────
    detected_mime = detect_mime_type(file_bytes)
    valid, err = validate_mime_against_extension(detected_mime, ext)
    if not valid:
        raise ValueError(f"File content validation failed: {err}")

    # ── 5. Calculate SHA-256 of original plaintext ─────────────────────────
    sha256 = calculate_sha256(file_bytes)

    # ── 6. Encrypt with AES-256-GCM ───────────────────────────────────────
    ciphertext, nonce_hex = encrypt_evidence(file_bytes)

    # ── 7. Write to secure storage with random filename ────────────────────
    storage_filename = generate_storage_filename(ext)
    storage_path = settings.evidence_storage_path / storage_filename

    with open(storage_path, "wb") as f:
        f.write(ciphertext)

    # ── 8. Persist metadata ────────────────────────────────────────────────
    evidence_number = _generate_evidence_number(db)

    evidence = Evidence(
        evidence_number=evidence_number,
        case_id=case.id,
        original_filename=filename,
        storage_filename=storage_filename,
        file_extension=ext,
        mime_type=detected_mime,
        file_size_bytes=len(file_bytes),
        sha256_hash=sha256,
        is_encrypted=True,
        encryption_algorithm="AES-256-GCM",
        encryption_nonce=nonce_hex,
        integrity_status=IntegrityStatus.PENDING,
        current_custodian_id=uploader.id,
        uploaded_by_id=uploader.id,
        status=EvidenceStatus.ACTIVE,
        description=description,
    )
    db.add(evidence)
    db.flush()  # get the ID

    # ── 9. Create chain-of-custody event ──────────────────────────────────
    now = datetime.now(timezone.utc)
    prev_hash, event_hash = _generate_custody_event_hash(
        db, evidence.id, CustodyAction.UPLOADED, uploader.id, now
    )
    custody = ChainOfCustody(
        evidence_id=evidence.id,
        case_id=case.id,
        actor_id=uploader.id,
        action=CustodyAction.UPLOADED,
        previous_custodian_id=None,
        new_custodian_id=uploader.id,
        reason="Initial evidence upload",
        timestamp=now,
        previous_event_hash=prev_hash,
        event_hash=event_hash,
        ip_address=ip_address,
    )
    db.add(custody)
    db.commit()
    db.refresh(evidence)

    # ── 10. Audit log ──────────────────────────────────────────────────────
    create_audit_log(
        db=db,
        action=AuditAction.EVIDENCE_UPLOADED,
        user=uploader,
        resource_type="evidence",
        resource_id=str(evidence.id),
        details=f"Evidence {evidence_number} uploaded to case {case.case_number}. SHA-256: {sha256}",
        ip_address=ip_address,
    )

    return evidence


def verify_evidence_integrity(
    db: Session,
    evidence: Evidence,
    requestor: User,
    ip_address: Optional[str],
) -> dict:
    """
    Integrity verification:
    1. Retrieve encrypted file from storage
    2. Decrypt using stored nonce
    3. Calculate SHA-256 of decrypted bytes
    4. Compare with stored hash
    5. Update integrity status
    6. Record custody event + audit log
    """
    storage_path = settings.evidence_storage_path / evidence.storage_filename

    if not storage_path.exists():
        _record_integrity_failure(db, evidence, requestor, ip_address)
        return {
            "evidence_id": evidence.id,
            "evidence_number": evidence.evidence_number,
            "original_filename": evidence.original_filename,
            "stored_hash": evidence.sha256_hash,
            "computed_hash": "MISSING_FILE",
            "match": False,
            "status": "INTEGRITY_FAILURE — EVIDENCE FILE MISSING",
            "verified_at": datetime.now(timezone.utc),
            "verified_by": requestor.username,
        }

    with open(storage_path, "rb") as f:
        ciphertext = f.read()

    from cryptography.exceptions import InvalidTag

    try:
        plaintext = decrypt_evidence(ciphertext, evidence.encryption_nonce)
    except InvalidTag:
        # Ciphertext authentication tag failed — tampered file
        _record_integrity_failure(db, evidence, requestor, ip_address)
        return {
            "evidence_id": evidence.id,
            "evidence_number": evidence.evidence_number,
            "original_filename": evidence.original_filename,
            "stored_hash": evidence.sha256_hash,
            "computed_hash": "DECRYPTION_FAILED",
            "match": False,
            "status": "INTEGRITY_FAILURE — AES-GCM AUTHENTICATION FAILED (TAMPERED)",
            "verified_at": datetime.now(timezone.utc),
            "verified_by": requestor.username,
        }
    except ValueError as e:
        err_msg = str(e)
        if "must decode to exactly 32 bytes" in err_msg or "ENCRYPTION_KEY" in err_msg:
            status_msg = "INTEGRITY_FAILURE — INVALID OR MISSING KEY CONFIGURATION"
        else:
            status_msg = "INTEGRITY_FAILURE — INVALID NONCE OR DECRYPTION ERROR"
        
        _record_integrity_failure(db, evidence, requestor, ip_address)
        return {
            "evidence_id": evidence.id,
            "evidence_number": evidence.evidence_number,
            "original_filename": evidence.original_filename,
            "stored_hash": evidence.sha256_hash,
            "computed_hash": "DECRYPTION_FAILED",
            "match": False,
            "status": status_msg,
            "verified_at": datetime.now(timezone.utc),
            "verified_by": requestor.username,
        }
    except Exception as e:
        status_msg = "INTEGRITY_FAILURE — UNKNOWN DECRYPTION ERROR"
        _record_integrity_failure(db, evidence, requestor, ip_address)
        return {
            "evidence_id": evidence.id,
            "evidence_number": evidence.evidence_number,
            "original_filename": evidence.original_filename,
            "stored_hash": evidence.sha256_hash,
            "computed_hash": "DECRYPTION_FAILED",
            "match": False,
            "status": status_msg,
            "verified_at": datetime.now(timezone.utc),
            "verified_by": requestor.username,
        }

    computed_hash = calculate_sha256(plaintext)
    match = computed_hash == evidence.sha256_hash

    # Update integrity status
    evidence.integrity_status = IntegrityStatus.VERIFIED if match else IntegrityStatus.FAILED
    evidence.last_verified_at = datetime.now(timezone.utc)
    db.add(evidence)

    # Custody event
    now = datetime.now(timezone.utc)
    prev_hash, event_hash = _generate_custody_event_hash(
        db, evidence.id, CustodyAction.VERIFIED, requestor.id, now
    )
    custody = ChainOfCustody(
        evidence_id=evidence.id,
        case_id=evidence.case_id,
        actor_id=requestor.id,
        action=CustodyAction.VERIFIED,
        previous_custodian_id=evidence.current_custodian_id,
        new_custodian_id=evidence.current_custodian_id,
        reason="Integrity verification performed",
        timestamp=now,
        previous_event_hash=prev_hash,
        event_hash=event_hash,
        ip_address=ip_address,
    )
    db.add(custody)
    db.commit()

    if not match:
        _record_integrity_failure(db, evidence, requestor, ip_address)

    create_audit_log(
        db=db,
        action=AuditAction.EVIDENCE_VERIFIED,
        user=requestor,
        resource_type="evidence",
        resource_id=str(evidence.id),
        details=f"Integrity check for {evidence.evidence_number}. Match: {match}. Computed: {computed_hash}",
        ip_address=ip_address,
        is_security_event=not match,
    )

    status_str = "HASH MATCH — INTEGRITY VERIFIED" if match else "INTEGRITY FAILURE — POSSIBLE TAMPERING DETECTED"

    return {
        "evidence_id": evidence.id,
        "evidence_number": evidence.evidence_number,
        "original_filename": evidence.original_filename,
        "stored_hash": evidence.sha256_hash,
        "computed_hash": computed_hash,
        "match": match,
        "status": status_str,
        "verified_at": datetime.now(timezone.utc),
        "verified_by": requestor.username,
    }


def _record_integrity_failure(db: Session, evidence: Evidence, user: User, ip: Optional[str]):
    """Create a security event for detected integrity failure."""
    from app.models.models import SecurityEvent
    event = SecurityEvent(
        event_type="EVIDENCE_INTEGRITY_FAILURE",
        severity="CRITICAL",
        source_ip=ip,
        user_id=user.id,
        description=f"Integrity failure detected for evidence {evidence.evidence_number}",
        details=f"Evidence ID: {evidence.id}, Case: {evidence.case_id}",
    )
    db.add(event)
    db.commit()


def transfer_evidence(
    db: Session,
    evidence: Evidence,
    from_user: User,
    to_user: User,
    reason: str,
    notes: Optional[str],
    ip_address: Optional[str],
) -> ChainOfCustody:
    """Transfer evidence custody from one user to another."""
    now = datetime.now(timezone.utc)
    prev_custodian_id = evidence.current_custodian_id

    # Record transfer in custody chain
    prev_hash, event_hash = _generate_custody_event_hash(
        db, evidence.id, CustodyAction.TRANSFERRED, from_user.id, now
    )
    custody = ChainOfCustody(
        evidence_id=evidence.id,
        case_id=evidence.case_id,
        actor_id=from_user.id,
        action=CustodyAction.TRANSFERRED,
        previous_custodian_id=prev_custodian_id,
        new_custodian_id=to_user.id,
        reason=reason,
        notes=notes,
        timestamp=now,
        previous_event_hash=prev_hash,
        event_hash=event_hash,
        ip_address=ip_address,
    )
    db.add(custody)

    evidence.current_custodian_id = to_user.id
    evidence.status = EvidenceStatus.TRANSFERRED
    db.add(evidence)
    db.commit()
    db.refresh(custody)

    create_audit_log(
        db=db,
        action=AuditAction.EVIDENCE_TRANSFERRED,
        user=from_user,
        resource_type="evidence",
        resource_id=str(evidence.id),
        details=f"Evidence {evidence.evidence_number} transferred to {to_user.username}. Reason: {reason}",
        ip_address=ip_address,
    )

    return custody


def receive_evidence(
    db: Session,
    evidence: Evidence,
    receiver: User,
    ip_address: Optional[str],
) -> ChainOfCustody:
    """Confirm receipt of evidence by the new custodian."""
    now = datetime.now(timezone.utc)
    prev_hash, event_hash = _generate_custody_event_hash(
        db, evidence.id, CustodyAction.RECEIVED, receiver.id, now
    )
    custody = ChainOfCustody(
        evidence_id=evidence.id,
        case_id=evidence.case_id,
        actor_id=receiver.id,
        action=CustodyAction.RECEIVED,
        previous_custodian_id=evidence.current_custodian_id,
        new_custodian_id=receiver.id,
        reason="Evidence received and confirmed",
        timestamp=now,
        previous_event_hash=prev_hash,
        event_hash=event_hash,
        ip_address=ip_address,
    )
    db.add(custody)

    # Mark active again after receipt confirmation
    evidence.status = EvidenceStatus.ACTIVE
    db.add(evidence)
    db.commit()
    db.refresh(custody)

    create_audit_log(
        db=db,
        action=AuditAction.EVIDENCE_RECEIVED,
        user=receiver,
        resource_type="evidence",
        resource_id=str(evidence.id),
        details=f"Evidence {evidence.evidence_number} received by {receiver.username}",
        ip_address=ip_address,
    )

    return custody
