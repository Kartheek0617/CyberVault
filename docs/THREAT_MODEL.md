# CyberVault Formal Threat Model (STRIDE)

## 1. Spoofing
- **Asset:** JWT Tokens & Login Endpoint
- **Attack Surface:** Authentication API
- **Impact:** Attacker logs in as victim.
- **Mitigation:** JWTs are heavily secured using HS256 with a 64-byte secret key and 30-min expiry. Passwords hashed using Bcrypt.
- **Verification:** Unit tests covering token validation and tampering signatures (in `test_security_comprehensive.py`).

## 2. Tampering
- **Asset:** Encrypted Evidence & Audit Logs
- **Attack Surface:** Filesystem and SQLite Database
- **Impact:** Attacker alters evidence or modifies log history to hide tracks.
- **Mitigation:** 
  1. Evidence is protected by AES-256-GCM (authentication tag prevents tampering).
  2. Audit Logs use cryptographic Hash Chaining (a broken link exposes tampering).
- **Verification:** Tests explicitly tamper with ciphertext and nonce expecting `InvalidTag` exceptions.

## 3. Repudiation
- **Asset:** Chain of Custody (CoC)
- **Attack Surface:** Transfer Endpoints
- **Impact:** An investigator claims they never possessed malware evidence.
- **Mitigation:** System inherently ties user UUIDs to CoC transfers via JWT extraction; no client-side spoofing possible. Ed25519 signatures finalize reports.
- **Verification:** Tested via End-to-End CoC sequences.

## 4. Information Disclosure
- **Asset:** Evidence Ciphertext & Encryption Keys
- **Attack Surface:** Hardcoded Configs, Open Ports, Git Repos
- **Impact:** PII and Case Files leaked.
- **Mitigation:** Strict `.env` usage. Config validates `ENCRYPTION_KEY` isn't missing. Directory structures restricted (`/app/evidence_storage` chown). Global exception handlers hide stack traces from users. 
- **Verification:** Environment config fail-safes added to `main.py` and `config.py`. 

## 5. Denial of Service (DoS)
- **Asset:** API / Database
- **Attack Surface:** File Upload API
- **Impact:** Disk exhaustion.
- **Mitigation:** Strict filesize and MIME/Extension validations. Rate limits on login attempts.
- **Verification:** Validations in `file_validation.py` and fast failure upon massive payload (FastAPI standard max upload handles).

## 6. Elevation of Privilege
- **Asset:** Investigator Role
- **Attack Surface:** JWT manipulation, IDOR / BOLA endpoints.
- **Impact:** Standard user acts as Admin or accesses unassigned cases.
- **Mitigation:** Deep RBAC checks in dependencies (`require_role`, `verify_case_access`). Validation of Case UUID mapping to User UUID.
- **Verification:** IDOR/BOLA attempts explicitly unit-tested to return 403.

## ASTRIDE Applicability
ASTRIDE was reviewed but is currently not applicable because CyberVault does not contain an AI agent. No AI-driven autonomous decisions, prompt interfaces, or LLM tools are present in the current architecture.
