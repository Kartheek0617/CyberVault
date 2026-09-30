"""
CyberVault — Database seed script.
Creates fictional demo data for all roles.
IMPORTANT: These are FICTIONAL accounts for demonstration only.
"""
import json
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, engine, Base
from app.models.models import (
    AuditAction, Case, CaseMember, CaseStatus, CasePriority, CaseType,
    ChainOfCustody, CustodyAction, Evidence, EvidenceStatus,
    IntegrityStatus, SecurityEvent, User, UserRole
)
from app.security.encryption import (
    calculate_sha256, encrypt_evidence, generate_event_hash,
    generate_storage_filename
)
from app.security.password import hash_password
from app.services.audit_service import create_audit_log

EVIDENCE_STORAGE = Path("./evidence_storage")
EVIDENCE_STORAGE.mkdir(parents=True, exist_ok=True)


def seed():
    print("[*] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("[*] Checking for existing data...")
    if db.query(User).count() > 0:
        print("[!] Database already has data. Skipping seed. Use --force to re-seed.")
        if "--force" not in sys.argv:
            db.close()
            return
        print("[!] Force flag detected. Clearing existing data...")
        db.query(Evidence).delete()
        db.query(ChainOfCustody).delete()
        db.query(CaseMember).delete()
        db.query(Case).delete()
        db.query(User).delete()
        db.commit()

    print("[*] Seeding fictional demo users...")

    # ── Users ──────────────────────────────────────────────────────────────
    admin = User(
        username="admin",
        email="admin@cybervault.demo",
        full_name="System Administrator",
        password_hash=hash_password("Admin@CyberVault2026!"),
        role=UserRole.ADMIN,
        badge_number="ADM-001",
        department="IT Security",
        is_active=True,
    )

    investigator1 = User(
        username="inv_harrison",
        email="j.harrison@cybervault.demo",
        full_name="Detective James Harrison",
        password_hash=hash_password("Invest@Vault2026!"),
        role=UserRole.INVESTIGATOR,
        badge_number="INV-004",
        department="Cybercrime Division",
        is_active=True,
    )

    investigator2 = User(
        username="inv_patel",
        email="s.patel@cybervault.demo",
        full_name="Detective Sarah Patel",
        password_hash=hash_password("Invest@Patel2026!"),
        role=UserRole.INVESTIGATOR,
        badge_number="INV-007",
        department="Digital Forensics",
        is_active=True,
    )

    custodian = User(
        username="cust_morgan",
        email="t.morgan@cybervault.demo",
        full_name="Thomas Morgan",
        password_hash=hash_password("Custodian@2026!"),
        role=UserRole.EVIDENCE_CUSTODIAN,
        badge_number="CUST-002",
        department="Evidence Management",
        is_active=True,
    )

    auditor = User(
        username="auditor_chen",
        email="l.chen@cybervault.demo",
        full_name="Lisa Chen",
        password_hash=hash_password("Auditor@Vault2026!"),
        role=UserRole.AUDITOR,
        badge_number="AUD-001",
        department="Internal Audit",
        is_active=True,
    )

    for u in [admin, investigator1, investigator2, custodian, auditor]:
        db.add(u)
    db.flush()

    print("[*] Seeding fictional cases...")

    # ── Cases ──────────────────────────────────────────────────────────────
    case1 = Case(
        case_number="CASE-2026-001",
        title="Unauthorized System Access — FinTech Corp",
        description="Investigation into unauthorized access of internal banking servers at FinTech Corp. Multiple failed authentication attempts detected from external IPs. Suspected nation-state actor involvement.",
        case_type=CaseType.NETWORK_INTRUSION,
        priority=CasePriority.CRITICAL,
        status=CaseStatus.ACTIVE,
        created_by_id=investigator1.id,
    )

    case2 = Case(
        case_number="CASE-2026-002",
        title="Ransomware Attack — MediCore Hospital Systems",
        description="Ransomware deployment across MediCore's internal network affecting patient record systems. Initial vector suspected to be phishing email attachment. Forensic analysis of affected endpoints required.",
        case_type=CaseType.MALWARE,
        priority=CasePriority.HIGH,
        status=CaseStatus.ACTIVE,
        created_by_id=investigator2.id,
    )

    case3 = Case(
        case_number="CASE-2026-003",
        title="Insider Data Exfiltration — TechDynamics Inc",
        description="Former employee suspected of exfiltrating proprietary source code and customer data via USB drives and personal cloud storage accounts prior to resignation.",
        case_type=CaseType.INSIDER_THREAT,
        priority=CasePriority.HIGH,
        status=CaseStatus.ACTIVE,
        created_by_id=investigator1.id,
    )

    for c in [case1, case2, case3]:
        db.add(c)
    db.flush()

    # ── Case Members ───────────────────────────────────────────────────────
    members = [
        CaseMember(case_id=case1.id, user_id=investigator1.id, role_in_case="LEAD_INVESTIGATOR"),
        CaseMember(case_id=case1.id, user_id=investigator2.id, role_in_case="DIGITAL_FORENSICS"),
        CaseMember(case_id=case2.id, user_id=investigator2.id, role_in_case="LEAD_INVESTIGATOR"),
        CaseMember(case_id=case2.id, user_id=investigator1.id, role_in_case="SUPPORT"),
        CaseMember(case_id=case3.id, user_id=investigator1.id, role_in_case="LEAD_INVESTIGATOR"),
    ]
    for m in members:
        db.add(m)
    db.flush()

    print("[*] Seeding fictional evidence with real encryption...")

    # ── Evidence with real AES-256-GCM encryption ──────────────────────────
    evidence_data = [
        {
            "case": case1,
            "uploader": investigator1,
            "filename": "network_capture_2026-09-14.pcap",
            "content": b"FICTIONAL PCAP CONTENT: TCP SYN flood detected from 198.51.100.42. Port 22 brute force. 4729 failed auth attempts in 180 seconds. [DEMO DATA - NOT REAL]",
            "mime_type": "application/vnd.tcpdump.pcap",
            "description": "Network packet capture during the incident window showing suspicious connection patterns",
        },
        {
            "case": case1,
            "uploader": investigator2,
            "filename": "server_access_log_excerpt.txt",
            "content": b"FICTIONAL LOG: 2026-09-14 02:31:17 FAILED_LOGIN root FROM 198.51.100.42\n2026-09-14 02:31:18 FAILED_LOGIN admin FROM 198.51.100.42\n[DEMO DATA - NOT REAL]",
            "mime_type": "text/plain",
            "description": "Server authentication log showing brute force attempts",
        },
        {
            "case": case2,
            "uploader": investigator2,
            "filename": "ransomware_sample_metadata.txt",
            "content": b"FICTIONAL MALWARE METADATA: SHA256: DEMO_HASH_ONLY. File: invoice.pdf.exe. Mutex: Global\\XWorm_v2.1. C2: 203.0.113.99:4444. [DEMO DATA - NOT REAL]",
            "mime_type": "text/plain",
            "description": "Metadata extracted from ransomware sample found on compromised endpoint",
        },
        {
            "case": case3,
            "uploader": investigator1,
            "filename": "usb_activity_report.csv",
            "content": b"FICTIONAL CSV:\nTimestamp,Device,Action,FileCount\n2026-09-10 17:45:00,USB_WD_1TB,CONNECTED,0\n2026-09-10 17:47:32,USB_WD_1TB,COPY,1247\n[DEMO DATA - NOT REAL]",
            "mime_type": "text/plain",
            "description": "USB device activity log from HR department workstation",
        },
    ]

    evidence_objects = []
    ev_counter = 1
    year = 2026

    for idx, ed in enumerate(evidence_data):
        file_bytes = ed["content"]
        sha256 = calculate_sha256(file_bytes)
        ciphertext, nonce_hex = encrypt_evidence(file_bytes)

        storage_fn = generate_storage_filename(".enc")
        with open(EVIDENCE_STORAGE / storage_fn, "wb") as f:
            f.write(ciphertext)

        ext = "." + ed["filename"].rsplit(".", 1)[-1]
        ev = Evidence(
            evidence_number=f"EV-{year}-{ev_counter:04d}",
            case_id=ed["case"].id,
            original_filename=ed["filename"],
            storage_filename=storage_fn,
            file_extension=ext,
            mime_type=ed["mime_type"],
            file_size_bytes=len(file_bytes),
            sha256_hash=sha256,
            is_encrypted=True,
            encryption_algorithm="AES-256-GCM",
            encryption_nonce=nonce_hex,
            integrity_status=IntegrityStatus.VERIFIED,
            current_custodian_id=ed["uploader"].id,
            uploaded_by_id=ed["uploader"].id,
            status=EvidenceStatus.ACTIVE,
            description=ed["description"],
        )
        db.add(ev)
        db.flush()
        evidence_objects.append(ev)
        ev_counter += 1

    db.flush()

    print("[*] Seeding chain-of-custody events...")

    # ── Chain of Custody Events ────────────────────────────────────────────
    prev_hash = None
    for ev in evidence_objects:
        now = datetime.now(timezone.utc) - timedelta(hours=len(evidence_objects) - evidence_objects.index(ev))
        event_data = json.dumps({
            "evidence_id": str(ev.id),
            "action": CustodyAction.UPLOADED.value,
            "actor_id": str(ev.uploaded_by_id),
            "timestamp": now.isoformat(),
        }, sort_keys=True)
        current_hash = generate_event_hash(prev_hash, event_data)

        custody = ChainOfCustody(
            evidence_id=ev.id,
            case_id=ev.case_id,
            actor_id=ev.uploaded_by_id,
            action=CustodyAction.UPLOADED,
            new_custodian_id=ev.uploaded_by_id,
            reason="Initial evidence upload",
            timestamp=now,
            previous_event_hash=prev_hash,
            event_hash=current_hash,
        )
        db.add(custody)
        prev_hash = current_hash

    db.flush()

    print("[*] Seeding audit log entries...")

    # Seed a few initial audit entries
    for u in [admin, investigator1, investigator2, custodian, auditor]:
        create_audit_log(
            db=db,
            action=AuditAction.USER_CREATED,
            user=admin,
            resource_type="user",
            resource_id=str(u.id),
            details=f"Demo user {u.username} created during system initialization",
        )

    for c in [case1, case2, case3]:
        create_audit_log(
            db=db,
            action=AuditAction.CASE_CREATED,
            user=investigator1,
            resource_type="case",
            resource_id=str(c.id),
            details=f"Case {c.case_number} created: {c.title}",
        )

    db.commit()
    db.close()

    print("\n" + "="*60)
    print("✓ CyberVault Demo Database Seeded Successfully")
    print("="*60)
    print("\n[DEMO CREDENTIALS — FICTIONAL ACCOUNTS ONLY]")
    print(f"  Admin:      admin / Admin@CyberVault2026!")
    print(f"  Investigator 1: inv_harrison / Invest@Vault2026!")
    print(f"  Investigator 2: inv_patel / Invest@Patel2026!")
    print(f"  Custodian:  cust_morgan / Custodian@2026!")
    print(f"  Auditor:    auditor_chen / Auditor@Vault2026!")
    print("\n[WARNING] Never use these credentials in a real system.")
    print("="*60)


if __name__ == "__main__":
    seed()
