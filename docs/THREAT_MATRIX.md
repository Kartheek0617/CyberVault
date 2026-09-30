# CyberVault Threat Matrix (STRIDE)

| Threat ID | Component | Asset/Data Flow | STRIDE | Threat | Attack Scenario | Impact | Likelihood | Risk | Existing Mitigation | Additional Mitigation | Security Test |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TM-01 | API | Login Context | Spoofing | Auth Bypass | Attacker intercepts/modifies JWT token payload. | HIGH | LOW | MEDIUM | JWT HS256, 64-byte secret key, short expiry. | Implement hardware tokens (FIDO2) | `test_auth_invalid_token` |
| TM-02 | File System | Evidence File | Tampering | Ciphertext modification | Attacker compromises OS and flips bits on disk. | HIGH | LOW | MEDIUM | AES-GCM Integrity Auth Tag. | OS-level FIM (File Integrity Monitoring) | `test_crypto_ciphertext_modification` |
| TM-03 | Database | Audit Ledger | Tampering | Log destruction | Malicious admin attempts to cover tracks by deleting DB rows. | HIGH | LOW | MEDIUM | Sequential cryptographic Hash Chaining on `AuditLog`. | Remote syslog forwarding | `test_audit_historical_modification` |
| TM-04 | API | Custody Endpoints| Repudiation | Deny custody | Investigator claims malware was never downloaded. | HIGH | LOW | MEDIUM | CoC tightly coupled to JWT server-side, Ed25519 digital signatures. | None | `test_coc_valid_transfer` |
| TM-05 | Env Configs | `ENCRYPTION_KEY` | Info Disc. | Key leakage | API exposes environment variables in 500 error trace. | CRIT | LOW | HIGH | Global exception handlers prevent stack traces. Strict `.env` parsing. | Secrets vault (HashiCorp) | Manual Fuzzing / Code Review |
| TM-06 | File API | File Upload | DoS | Disk Exhaustion | Attacker uploads massive or infinite looping file. | MED | MED | MEDIUM | Size bounds, MIME type checking via python-magic, extension strictness. | Rate limiting per user | `test_file_oversized` |
| TM-07 | API | Cases API | Elevation | IDOR / BOLA | User 1 passes `case_id` belonging to User 2 to view unauthorized dataset. | HIGH | MED | HIGH | JWT UUID extraction heavily cross-verified against `CaseMember` table bounds. | None | `test_authz_idor_bola` |
