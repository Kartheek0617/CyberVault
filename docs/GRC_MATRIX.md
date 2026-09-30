# CyberVault GRC Matrix (Governance, Risk, and Compliance)

| Control ID | Security Requirement | Risk | Control | Implementation | Evidence | Test | Responsible Role | Status |
|---|---|---|---|---|---|---|---|---|
| CTL-01 | SEC-01: Encrypt at rest | Theft of raw evidence disk | AES-256-GCM cryptography | `crypto_service.py` | `.enc` extension | `test_crypto_encrypt_decrypt` | Investigator | IMPLEMENTED |
| CTL-02 | SEC-04: Immutable Ledgers | Admin manipulating evidence logs | SHA-256 Hash Chaining | `audit_service.py` | API validation | `test_audit_historical_modification`| Auditor | IMPLEMENTED |
| CTL-03 | SEC-03: Strict Authorization | IDOR exploitation across cases | Context Binders / JWT | `case_service.py` | Code hooks | `test_authz_idor_bola` | Application Core | IMPLEMENTED |
| CTL-04 | NFR-01: Isolated Secrets | Leakage of Encryption keys | Environment Variable loading | `config.py` | `.env` omission | `test_crypto_wrong_key` | DevOps / SysAdmin | IMPLEMENTED |
| CTL-05 | FR-03: Restrict File Uploads | RCE / Path Traversal | Python-magic MIME mapping | `file_validation.py` | Validation Drop | `test_file_filename_traversal` | App Core | IMPLEMENTED |

**Disclaimer:** These controls are *Aligned with security practice* for law enforcement chain-of-custody data, but do not inherently constitute verified legal regulatory compliance without third-party audit.
