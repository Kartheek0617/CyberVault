"""
CyberVault — All SQLAlchemy ORM models.
Security design: models use UUIDs, proper constraints, and no sensitive data leakage.
"""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey,
    Index, Integer, String, Text, UniqueConstraint, Uuid as SA_Uuid
)
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import relationship

from app.core.database import Base


class UuidSafe(TypeDecorator):
    """
    Custom Uuid implementation that safely accepts both Python UUID objects and valid
    UUID strings. Converts strings to uuid.UUID before they reach SA_Uuid, preventing
    AttributeError: 'str' object has no attribute 'hex' internally.
    """
    impl = SA_Uuid
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                value = uuid.UUID(value)
            except ValueError:
                pass
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return uuid.UUID(value)
            except ValueError:
                pass
        return value

# Override Uuid so model columns continue to use this custom safe UUID type.
Uuid = UuidSafe
def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    INVESTIGATOR = "INVESTIGATOR"
    EVIDENCE_CUSTODIAN = "EVIDENCE_CUSTODIAN"
    AUDITOR = "AUDITOR"


class CaseStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"
    PENDING = "PENDING"


class CasePriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CaseType(str, enum.Enum):
    CYBERCRIME = "CYBERCRIME"
    FRAUD = "FRAUD"
    DATA_BREACH = "DATA_BREACH"
    MALWARE = "MALWARE"
    NETWORK_INTRUSION = "NETWORK_INTRUSION"
    INSIDER_THREAT = "INSIDER_THREAT"
    OTHER = "OTHER"


class EvidenceStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    TRANSFERRED = "TRANSFERRED"
    ARCHIVED = "ARCHIVED"
    COMPROMISED = "COMPROMISED"


class IntegrityStatus(str, enum.Enum):
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    PENDING = "PENDING"


class CustodyAction(str, enum.Enum):
    UPLOADED = "UPLOADED"
    VERIFIED = "VERIFIED"
    VIEWED = "VIEWED"
    TRANSFER_REQUESTED = "TRANSFER_REQUESTED"
    TRANSFERRED = "TRANSFERRED"
    RECEIVED = "RECEIVED"
    RETURNED = "RETURNED"
    ARCHIVED = "ARCHIVED"
    INTEGRITY_CHECK = "INTEGRITY_CHECK"


class AuditAction(str, enum.Enum):
    USER_LOGIN = "USER_LOGIN"
    USER_LOGIN_FAILED = "USER_LOGIN_FAILED"
    USER_LOGOUT = "USER_LOGOUT"
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DISABLED = "USER_DISABLED"
    CASE_CREATED = "CASE_CREATED"
    CASE_UPDATED = "CASE_UPDATED"
    CASE_VIEWED = "CASE_VIEWED"
    EVIDENCE_UPLOADED = "EVIDENCE_UPLOADED"
    EVIDENCE_VIEWED = "EVIDENCE_VIEWED"
    EVIDENCE_DOWNLOADED = "EVIDENCE_DOWNLOADED"
    EVIDENCE_VERIFIED = "EVIDENCE_VERIFIED"
    EVIDENCE_TRANSFER_REQUESTED = "EVIDENCE_TRANSFER_REQUESTED"
    EVIDENCE_TRANSFERRED = "EVIDENCE_TRANSFERRED"
    EVIDENCE_RECEIVED = "EVIDENCE_RECEIVED"
    REPORT_GENERATED = "REPORT_GENERATED"
    REPORT_SIGNED = "REPORT_SIGNED"
    SIGNATURE_VERIFIED = "SIGNATURE_VERIFIED"
    AUDIT_VERIFIED = "AUDIT_VERIFIED"
    ACCESS_DENIED = "ACCESS_DENIED"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    INTEGRITY_FAILURE = "INTEGRITY_FAILURE"


# ─────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    # Argon2id hash — never store plaintext
    password_hash = Column(String(512), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.INVESTIGATOR)
    is_active = Column(Boolean, nullable=False, default=True)
    badge_number = Column(String(20), unique=True, nullable=True)
    department = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    created_cases = relationship("Case", back_populates="creator", foreign_keys="Case.created_by_id")
    case_memberships = relationship("CaseMember", back_populates="user")
    custody_events = relationship("ChainOfCustody", back_populates="actor", foreign_keys="ChainOfCustody.actor_id")
    audit_logs = relationship("AuditLog", back_populates="user")
    reports = relationship("Report", back_populates="generated_by_user")

    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"


class Case(Base):
    __tablename__ = "cases"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    case_number = Column(String(30), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    case_type = Column(Enum(CaseType), nullable=False)
    priority = Column(Enum(CasePriority), nullable=False, default=CasePriority.MEDIUM)
    status = Column(Enum(CaseStatus), nullable=False, default=CaseStatus.ACTIVE)
    created_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    creator = relationship("User", back_populates="created_cases", foreign_keys=[created_by_id])
    members = relationship("CaseMember", back_populates="case")
    evidence_items = relationship("Evidence", back_populates="case")
    reports = relationship("Report", back_populates="case")

    __table_args__ = (
        Index("ix_cases_status", "status"),
        Index("ix_cases_created_at", "created_at"),
    )


class CaseMember(Base):
    __tablename__ = "case_members"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    case_id = Column(Uuid(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_in_case = Column(String(50), nullable=True)
    added_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    case = relationship("Case", back_populates="members")
    user = relationship("User", back_populates="case_memberships")

    __table_args__ = (
        UniqueConstraint("case_id", "user_id", name="uq_case_member"),
    )


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    evidence_number = Column(String(30), unique=True, nullable=False, index=True)
    case_id = Column(Uuid(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    # Original filename stored as metadata ONLY — never used as a filesystem path
    original_filename = Column(String(255), nullable=False)
    # Cryptographically random internal storage filename
    storage_filename = Column(String(255), unique=True, nullable=False)
    file_extension = Column(String(20), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    # SHA-256 of the ORIGINAL (pre-encryption) file
    sha256_hash = Column(String(64), nullable=False)
    # Encryption metadata
    is_encrypted = Column(Boolean, nullable=False, default=True)
    encryption_algorithm = Column(String(30), nullable=False, default="AES-256-GCM")
    # Nonce used for AES-GCM (hex-encoded), stored separately from file
    encryption_nonce = Column(String(64), nullable=False)
    # Integrity check status
    integrity_status = Column(Enum(IntegrityStatus), nullable=False, default=IntegrityStatus.PENDING)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    # Current custody
    current_custodian_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    uploaded_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(EvidenceStatus), nullable=False, default=EvidenceStatus.ACTIVE)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    # Relationships
    case = relationship("Case", back_populates="evidence_items")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])
    current_custodian = relationship("User", foreign_keys=[current_custodian_id])
    custody_chain = relationship("ChainOfCustody", back_populates="evidence", order_by="ChainOfCustody.timestamp")

    __table_args__ = (
        Index("ix_evidence_case_id", "case_id"),
        Index("ix_evidence_sha256", "sha256_hash"),
    )


class ChainOfCustody(Base):
    __tablename__ = "chain_of_custody"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    evidence_id = Column(Uuid(as_uuid=True), ForeignKey("evidence.id"), nullable=False)
    case_id = Column(Uuid(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    actor_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(Enum(CustodyAction), nullable=False)
    previous_custodian_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    new_custodian_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    # Hash-chaining for tamper detection
    previous_event_hash = Column(String(64), nullable=True)
    event_hash = Column(String(64), nullable=False)
    # IP of the actor (for audit)
    ip_address = Column(String(45), nullable=True)

    # Relationships
    evidence = relationship("Evidence", back_populates="custody_chain")
    actor = relationship("User", back_populates="custody_events", foreign_keys=[actor_id])
    previous_custodian = relationship("User", foreign_keys=[previous_custodian_id])
    new_custodian = relationship("User", foreign_keys=[new_custodian_id])

    __table_args__ = (
        Index("ix_coc_evidence_id", "evidence_id"),
        Index("ix_coc_timestamp", "timestamp"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    sequence_number = Column(Integer, nullable=False)  # monotonically increasing
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(Enum(AuditAction), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    # Hash-chain: SHA256(prev_hash + event_data) for tamper detection
    previous_hash = Column(String(64), nullable=True)
    current_hash = Column(String(64), nullable=False)
    is_security_event = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_timestamp", "timestamp"),
        Index("ix_audit_action", "action"),
        Index("ix_audit_user_id", "user_id"),
    )


class Report(Base):
    __tablename__ = "reports"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    report_number = Column(String(30), unique=True, nullable=False)
    case_id = Column(Uuid(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    generated_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    # JSON array of evidence IDs included in the report
    evidence_ids = Column(Text, nullable=False)  # stored as JSON
    # SHA-256 of the report content
    report_hash = Column(String(64), nullable=False)
    # Ed25519 digital signature (hex)
    digital_signature = Column(Text, nullable=True)
    signature_algorithm = Column(String(30), nullable=True, default="Ed25519")
    is_signed = Column(Boolean, default=False, nullable=False)
    # PDF blob path (if generated)
    pdf_storage_path = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    # Report content as JSON
    report_content = Column(Text, nullable=True)

    # Relationships
    case = relationship("Case", back_populates="reports")
    generated_by_user = relationship("User", back_populates="reports")
    signature = relationship("DigitalSignature", back_populates="report", uselist=False)


class DigitalSignature(Base):
    __tablename__ = "digital_signatures"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    report_id = Column(Uuid(as_uuid=True), ForeignKey("reports.id"), nullable=False, unique=True)
    signer_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    algorithm = Column(String(30), nullable=False, default="Ed25519")
    # Hex-encoded signature
    signature_hex = Column(Text, nullable=False)
    # Hex-encoded public key used at signing time (for archival non-repudiation)
    public_key_hex = Column(Text, nullable=False)
    signed_data_hash = Column(String(64), nullable=False)
    signed_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    is_valid = Column(Boolean, nullable=True)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    report = relationship("Report", back_populates="signature")
    signer = relationship("User")


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    event_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False, default="INFO")  # INFO, WARNING, CRITICAL
    source_ip = Column(String(45), nullable=True)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    description = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    resolved = Column(Boolean, default=False, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    __table_args__ = (
        Index("ix_security_events_timestamp", "timestamp"),
        Index("ix_security_events_severity", "severity"),
    )
