# CyberVault Security Architecture

## Subsystem Trust Boundaries

```text
User Request (Browser/API)
       │
       ▼  [Trust Boundary: network traversal]
+-----------------------------------+
|         Frontend (React)          |
+-----------------------------------+
       │  (HTTPS/WSS - Axios Calls)
       ▼  [Trust Boundary: API Edge]
+-----------------------------------+
|      FastAPI Application          |
|  - CORS Restrictions              |
|  - Security Headers (CSP, Frame)  |
+-----------------------------------+
       │
       ▼
+-----------------------------------+
|        Authentication             |
|  - BCrypt Hash Checks             |
|  - JWT HS256 Token Issuance       |
+-----------------------------------+
       │
       ▼
+-----------------------------------+
|          Authorization            |
|  - RBAC (Admin vs Investigator)   |
|  - Case-level Authorization       |
|  - IDOR / BOLA Protections        |
+-----------------------------------+
       │
       ▼  [Business Logic & Storage Boundaries]
+-----------------------------------+
|       Evidence Management         |
|  - File Validation (MIME / Ext)   |
|  - SHA-256 Hashing                |
|  - AES-256-GCM Encryption         |
+-----------------------------------+
       │
       ├─────────────────────────────────┐
       ▼                                 ▼
+-----------------------------+   +-----------------------------+
|    Encrypted File Store     |   |   SQLite Database           |
|  - Stored physically on HDD |   | - Metadata                  |
|  - Filenames as Random UUIDs|   | - Ed25519 Signed Reports    |
+-----------------------------+   +-----------------------------+
                                         │
                                         ▼
                                  +-----------------------------+
                                  |    Audit & Hash Chains      |
                                  | - Custody Event Tracking    |
                                  | - Linked SHA-256 validation |
                                  +-----------------------------+
```

## Security Controls Implemented
*(Aligned with mapped Data Flow Diagram in `docs/DFD.md`)*
1. **Network Security:** API endpoints hardened with Content-Security policies and CORS boundaries.
2. **Access Control:** Centralized dependency injection enforces RBAC inherently.
3. **Cryptography:** 
   - Evidence at Rest: AES-256-GCM (ensuring confidentiality & authenticity of ciphertext)
   - Evidence Integrity: SHA-256
   - Report Authenticity: Ed25519 Keypairs
4. **Resiliency:** Deterministic verification processes that dynamically detect SQLite level tampering.
