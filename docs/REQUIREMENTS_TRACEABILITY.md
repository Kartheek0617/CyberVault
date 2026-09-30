# CyberVault Requirements Traceability Matrix

| Requirement ID | Requirement | Source | Implementation | Security Control | Test Case | Result | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| FR-01 | JWT Authentication | SRS | `app/api/auth.py` | Rate limiting, HS256 signatures | `test_auth_invalid_token` | PASS | IMPLEMENTED | Passing Pytest logs |
| FR-02 | RBAC enforcement | SRS | `app/api/cases.py` | Dependency injection role-checker | `test_authz_role_restrictions` | PASS | IMPLEMENTED | Tests assert 403 Forbidden |
| FR-03 | Evidence Upload | SRS | `app/api/evidence.py` | File extension/MIME validation | `test_file_invalid_extension` | PASS | IMPLEMENTED | Traversal test drops |
| SEC-01 | Encrypt Evidence at Rest | Threat Model | `app/services/crypto_service.py` | AES-256-GCM | `test_crypto_encrypt_decrypt` | PASS | IMPLEMENTED | Disk file confirmed encrypted |
| SEC-02 | Ensure integrity on decrypt | Threat Model | `app/services/crypto_service.py` | GCM Auth Tag validation | `test_crypto_ciphertext_modification` | PASS | IMPLEMENTED | InvalidTag Exception triggers 400 |
| SEC-03 | Prevent IDOR/BOLA attacks | OWASP | `app/services/case_service.py` | DB context-bound lookups | `test_authz_idor_bola` | PASS | IMPLEMENTED | 403 returned on mismatch |
| SEC-04 | Hash-chained Audit Logs | GRC | `app/services/audit_service.py`| SHA-256 state linkage (`prev_hash`) | `test_audit_historical_modification` | PASS | IMPLEMENTED | Integrity failure on DB manipulation |
| SEC-05 | Digital Signatures for Reports | SRS | `app/services/report_service.py`| Ed25519 cryptography | `test_report_valid_signature` | PASS | IMPLEMENTED | `is_signed` boolean confirmed |
| SEC-06 | Non-transient AES Keys | Threat Model | `app/core/config.py` | Required `ENCRYPTION_KEY` via env | `test_crypto_restart_persistence` | PASS | IMPLEMENTED | Evidence decrypts post-restart |
