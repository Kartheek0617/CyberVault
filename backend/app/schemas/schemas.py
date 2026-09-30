"""
CyberVault — Pydantic schemas for request/response validation.
Security: Response schemas NEVER include password hashes, encryption keys, or private keys.
"""
import json
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.models import (
    AuditAction,
    CaseStatus,
    CasePriority,
    CaseType,
    CustodyAction,
    EvidenceStatus,
    IntegrityStatus,
    UserRole,
)


# ─────────────────────────────────────────────────────────────────────────────
# Auth Schemas
# ─────────────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str
    role: str
    full_name: str


# ─────────────────────────────────────────────────────────────────────────────
# User Schemas
# ─────────────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=150)
    password: str = Field(..., min_length=12)
    role: UserRole = UserRole.INVESTIGATOR
    badge_number: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    badge_number: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    badge_number: Optional[str]
    department: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int


# ─────────────────────────────────────────────────────────────────────────────
# Case Schemas
# ─────────────────────────────────────────────────────────────────────────────

class CaseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    case_type: CaseType
    priority: CasePriority = CasePriority.MEDIUM


class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    case_type: Optional[CaseType] = None
    priority: Optional[CasePriority] = None
    status: Optional[CaseStatus] = None


class CaseMemberAdd(BaseModel):
    user_id: UUID
    role_in_case: Optional[str] = Field(None, max_length=50)


class CaseResponse(BaseModel):
    id: UUID
    case_number: str
    title: str
    description: Optional[str]
    case_type: CaseType
    priority: CasePriority
    status: CaseStatus
    created_by_id: UUID
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]
    creator: Optional[UserResponse] = None
    member_count: Optional[int] = None
    evidence_count: Optional[int] = None

    model_config = {"from_attributes": True}


class CaseDetailResponse(CaseResponse):
    members: List[UserResponse] = []
    evidence_summary: List[dict] = []


# ─────────────────────────────────────────────────────────────────────────────
# Evidence Schemas
# ─────────────────────────────────────────────────────────────────────────────

class EvidenceMetadataResponse(BaseModel):
    id: UUID
    evidence_number: str
    case_id: UUID
    original_filename: str
    file_extension: str
    mime_type: str
    file_size_bytes: int
    sha256_hash: str
    is_encrypted: bool
    encryption_algorithm: str
    integrity_status: IntegrityStatus
    last_verified_at: Optional[datetime]
    current_custodian_id: Optional[UUID]
    uploaded_by_id: UUID
    status: EvidenceStatus
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    # Populated from relationships
    uploaded_by: Optional[UserResponse] = None
    current_custodian: Optional[UserResponse] = None

    model_config = {"from_attributes": True}


class EvidenceIntegrityResult(BaseModel):
    evidence_id: UUID
    evidence_number: str
    original_filename: str
    stored_hash: str
    computed_hash: str
    match: bool
    status: str  # "VERIFIED" or "INTEGRITY_FAILURE"
    verified_at: datetime
    verified_by: str


class EvidenceTransferRequest(BaseModel):
    to_user_id: UUID
    reason: str = Field(..., min_length=5, max_length=1000)
    notes: Optional[str] = Field(None, max_length=2000)


# ─────────────────────────────────────────────────────────────────────────────
# Chain of Custody Schemas
# ─────────────────────────────────────────────────────────────────────────────

class CustodyEventResponse(BaseModel):
    id: UUID
    evidence_id: UUID
    case_id: UUID
    action: CustodyAction
    reason: Optional[str]
    notes: Optional[str]
    timestamp: datetime
    previous_event_hash: Optional[str]
    event_hash: str
    actor: Optional[UserResponse] = None
    previous_custodian: Optional[UserResponse] = None
    new_custodian: Optional[UserResponse] = None

    model_config = {"from_attributes": True}


class CustodyChainResponse(BaseModel):
    evidence_id: UUID
    evidence_number: str
    events: List[CustodyEventResponse]
    total_events: int


# ─────────────────────────────────────────────────────────────────────────────
# Audit Log Schemas
# ─────────────────────────────────────────────────────────────────────────────

class AuditLogResponse(BaseModel):
    id: UUID
    sequence_number: int
    action: AuditAction
    resource_type: Optional[str]
    resource_id: Optional[str]
    details: Optional[str]
    ip_address: Optional[str]
    timestamp: datetime
    previous_hash: Optional[str] = None
    current_hash: Optional[str] = None
    is_security_event: bool
    user: Optional[UserResponse] = None
    user_id: Optional[UUID] = None

    # Computed aliases for frontend compatibility
    @property
    def entry_hash(self):
        return self.current_hash

    @property
    def previous_entry_hash(self):
        return self.previous_hash

    model_config = {"from_attributes": True}


class AuditIntegrityResult(BaseModel):
    total_entries: int
    invalid_entries: int
    first_tampering_sequence: Optional[int]
    is_valid: bool
    message: str
    checked_at: datetime


# ─────────────────────────────────────────────────────────────────────────────
# Report Schemas
# ─────────────────────────────────────────────────────────────────────────────

class ReportCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    evidence_ids: List[UUID]


class ReportResponse(BaseModel):
    id: UUID
    report_number: str
    case_id: UUID
    title: str
    report_hash: str
    digital_signature: Optional[str]
    signature_algorithm: Optional[str]
    is_signed: bool
    created_at: datetime
    generated_by_user: Optional[UserResponse] = None
    report_content: Optional[dict] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_content(cls, report):
        data = {
            "id": report.id,
            "report_number": report.report_number,
            "case_id": report.case_id,
            "title": report.title,
            "report_hash": report.report_hash,
            "digital_signature": report.digital_signature,
            "signature_algorithm": report.signature_algorithm,
            "is_signed": report.is_signed,
            "created_at": report.created_at,
            "generated_by_user": report.generated_by_user,
            "report_content": json.loads(report.report_content) if report.report_content else None,
        }
        return cls(**data)


class SignatureVerificationResult(BaseModel):
    report_id: UUID
    report_number: str
    is_valid: bool
    status: str  # "VALID" or "INVALID"
    signed_at: Optional[datetime]
    signer: Optional[str]
    algorithm: str
    verified_at: datetime


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard Schemas
# ─────────────────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    active_cases: int
    closed_cases: int
    total_evidence: int
    pending_transfers: int
    verified_evidence: int
    integrity_alerts: int
    total_users: int
    recent_security_events: int


class SecurityEventResponse(BaseModel):
    id: UUID
    event_type: str
    severity: str
    source_ip: Optional[str]
    description: str
    timestamp: datetime
    resolved: bool

    model_config = {"from_attributes": True}
