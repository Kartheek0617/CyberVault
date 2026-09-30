# CyberVault Security Testing

## 1. Authentication & Authorization
*   **TC-AUTH-01:** Valid Login. Expected: 200 OK + JWT. Status: Passing.
*   **TC-AUTH-02:** Invalid JWT. Expected: 401 Unauthorized. Status: Passing.
*   **TC-AUTHZ-01:** Role Restriction. Expected: User with 'auditor' role accessing 'admin' endpoints gets 403 Forbidden. Status: Passing.
*   **TC-AUTHZ-02:** IDOR on Case. Expected: Accessing case_id unassigned to User gets 403. Status: Passing.

## 2. File Security
*   **TC-FILE-01:** Invalid Extension (.exe). Expected: 400 Bad Request. Status: Passing.
*   **TC-FILE-02:** Filename Traversal (`../etc/passwd`). Expected: Sanitized/400. Status: Passing.
*   **TC-FILE-03:** MIME Mismatch. Expected: 400 Bad Request. Status: Passing.

## 3. Cryptography
*   **TC-CRYPT-01:** AES-GCM Encrypt/Decrypt matches plaintext exactly. Status: Passing.
*   **TC-CRYPT-02:** Persistent Key survival post-restart. Status: Passing.
*   **TC-CRYPT-03:** Ciphertext tampering triggers InvalidTag. Status: Passing.
*   **TC-CRYPT-04:** Nonce modification fails decryption. Status: Passing.
*   **TC-CRYPT-05:** SHA-256 match validation. Status: Passing.

## 4. Auditing & Custody
*   **TC-AUDIT-01:** Chain Validation computes current hash == stored hash. Status: Passing.
*   **TC-AUDIT-02:** Row modification (mimicking insider threat) triggers Tampered=True. Status: Passing.
*   **TC-COC-01:** Transfer evidence successfully creates CoC log. Status: Passing.

## 5. Reports
*   **TC-REPORT-01:** Report Ed25519 signature is valid. Status: Passing.
*   **TC-REPORT-02:** Modified report rejected on verification. Status: Passing.

## Execution
All tests are verified automatically via `.github/workflows/security-tests.yml` or locally via `pytest backend/tests/test_security_comprehensive.py`.
