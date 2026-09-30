# CyberVault Data Flow Diagram (DFD)

This logical DFD defines how data travels securely across trust boundaries within the CyberVault architecture.

## Level 0 (Context Diagram) Data Flow
- **External Entities:** Investigator, Administrator, Evidence Custodian, Auditor.
- **System:** CyberVault Secure Digital Evidence Management System.
- **Data Input:** Login Contexts, Digital Evidence (Raw Data), End-User Metadata.
- **Data Output:** Encrypted Assets, Hashes, PDF Reports, JWT Session Tokens.

## Level 1 Logical DFD Modules

### 1. Authentication Service
- **Input:** Credentials across HTTP request.
- **Process:** Verify Bcrypt, issue HS256 JWT containing User UUID and Roles.
- **Storage DB:** `Users` table (Read).
- **Security Control:** Rate limiter, TLS interception context.

### 2. Case Management
- **Input:** Case Creation / ACL mappings.
- **Process:** Checks JWT RBAC logic. Validates BOLA bounds on relations.
- **Storage DB:** `Cases`, `CaseMember` table (Write).

### 3. Evidence Upload & Encryption Service (Most Critical)
- **Input:** Multipart File Upload, Case UUID, JWT.
- **Process:**
  1. Validate file extension, MIME, limits.
  2. Stream bytes to memory, compute SHA-256 raw hash.
  3. Prepare AES-256-GCM symmetric session via `ENCRYPTION_KEY`.
  4. Encrypt file contents block-by-block, derive GCM Auth Tag.
  5. Assemble ChainOfCustody ledger entry.
- **Storage File:** `/evidence_storage/{random_uuid}.enc`
- **Storage DB:** `Evidence`, `ChainOfCustody` table (Write).
- **Security Boundary:** Frontend untrusted, Backend memory trusted, File System untrusted (ciphertext only).

### 4. Continuous Audit Logging
- **Input:** Business logic hooks spanning all service tiers.
- **Process:** Accepts log context, hashes previous log UUID + new log details.
- **Storage DB:** `AuditLog` table (Append Only).

### 5. Report & Signature Services
- **Input:** Aggregated JSON of case elements, Investigator Private Key parameters.
- **Process:** Extract case data, construct readable reporting JSON. Sign resulting bytes with Ed25519 payload.
- **Storage DB:** `Report`, `DigitalSignature` tables.

*See `docs/diagrams/cybervault-dfd.puml` for visual logical mapping.*
