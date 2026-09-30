"""
CyberVault — Audit logging service.
Implements a hash-chained, tamper-evident audit log.
Every write appends a new record; there is no update/delete for existing records in the normal API.
"""
import hashlib
import json
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.models import AuditAction, AuditLog, User
from app.security.encryption import generate_event_hash


def _build_audit_event_string(
    sequence_number: int,
    user_id: Optional[UUID],
    action: AuditAction,
    resource_type: Optional[str],
    resource_id: Optional[str],
    details: Optional[str],
    timestamp: datetime,
) -> str:
    """Canonical string representation of an audit event for hashing."""
    return json.dumps({
        "seq": sequence_number,
        "user_id": str(user_id) if user_id else None,
        "action": action.value,
        "resource_type": resource_type,
        "resource_id": str(resource_id) if resource_id else None,
        "details": details,
        "timestamp": timestamp.isoformat(),
    }, sort_keys=True)


def create_audit_log(
    db: Session,
    action: AuditAction,
    user: Optional[User] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    is_security_event: bool = False,
) -> AuditLog:
    """
    Append a new tamper-evident audit record.
    Computes the hash chain: SHA256(prev_hash + event_data).
    """
    # Get the last audit log entry for the hash chain
    last_entry = (
        db.query(AuditLog)
        .order_by(AuditLog.sequence_number.desc())
        .first()
    )

    prev_hash = last_entry.current_hash if last_entry else None
    sequence_number = (last_entry.sequence_number + 1) if last_entry else 1

    now = datetime.now(timezone.utc)
    user_id = user.id if user else None

    event_string = _build_audit_event_string(
        sequence_number=sequence_number,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        timestamp=now,
    )

    current_hash = generate_event_hash(prev_hash, event_string)

    log_entry = AuditLog(
        sequence_number=sequence_number,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        timestamp=now,
        previous_hash=prev_hash,
        current_hash=current_hash,
        is_security_event=is_security_event,
    )

    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def verify_audit_log_integrity(db: Session) -> dict:
    """
    Verify the entire audit log hash chain.
    Returns a dict with verification results.
    """
    entries = (
        db.query(AuditLog)
        .order_by(AuditLog.sequence_number.asc())
        .all()
    )

    now = datetime.now(timezone.utc)

    if not entries:
        return {
            "total_entries": 0,
            "invalid_entries": 0,
            "first_tampering_sequence": None,
            "is_valid": True,
            "message": "No audit records to verify.",
            "checked_at": now,
        }

    prev_hash = None
    for i, entry in enumerate(entries):
        expected_seq = i + 1
        if entry.sequence_number != expected_seq:
            return {
                "total_entries": len(entries),
                "invalid_entries": len(entries) - i,
                "first_tampering_sequence": entry.sequence_number,
                "is_valid": False,
                "message": f"Sequence gap detected at record {entry.sequence_number}. AUDIT LOG TAMPERING DETECTED.",
                "checked_at": now,
            }

        event_string = _build_audit_event_string(
            sequence_number=entry.sequence_number,
            user_id=entry.user_id,
            action=entry.action,
            resource_type=entry.resource_type,
            resource_id=entry.resource_id,
            details=entry.details,
            timestamp=entry.timestamp,
        )
        expected_hash = generate_event_hash(prev_hash, event_string)

        if entry.current_hash != expected_hash:
            return {
                "total_entries": len(entries),
                "invalid_entries": len(entries) - i,
                "first_tampering_sequence": entry.sequence_number,
                "is_valid": False,
                "message": f"Hash mismatch at sequence {entry.sequence_number}. AUDIT LOG TAMPERING DETECTED.",
                "checked_at": now,
            }

        if entry.previous_hash != prev_hash:
            return {
                "total_entries": len(entries),
                "invalid_entries": len(entries) - i,
                "first_tampering_sequence": entry.sequence_number,
                "is_valid": False,
                "message": f"Previous hash mismatch at sequence {entry.sequence_number}. AUDIT LOG TAMPERING DETECTED.",
                "checked_at": now,
            }

        prev_hash = entry.current_hash

    return {
        "total_entries": len(entries),
        "invalid_entries": 0,
        "first_tampering_sequence": None,
        "is_valid": True,
        "message": "AUDIT LOG INTEGRITY VERIFIED — All records are intact.",
        "checked_at": now,
    }
