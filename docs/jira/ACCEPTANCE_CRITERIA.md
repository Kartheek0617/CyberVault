# CyberVault Acceptance Criteria Examples

*This is a Jira-ready project artifact.*

## CV-14: Input File Validation
**Description:** As an investigator, I want my uploaded file metadata validated, so that malicious extensions and MIME spoofing attempts fail immediately.

**Acceptance Criteria:**
1. Given a user uploads a file, When the `.exe`, `.sh`, `.bat` extensions are used, Then the API throws a 400 Bad Request instantly.
2. Given a user uploads a `.pdf` file, When the internal Magic MIME buffer parses as `application/x-dosexec`, Then the upload is rejected.
3. Given a file payload, When the filename contains `../` or `/etc/`, Then it is stripped to a purely random UUID upon disk save.

## CV-15: AES-256-GCM Storage
**Description:** As a custodian, I want uploaded evidence forcibly encrypted via AES-256-GCM, so that data at rest is fundamentally immune to theft.

**Acceptance Criteria:**
1. Given a validated file upload, When writing to `/evidence_storage`, Then the physical file bytes MUST represent high-entropy ciphertext.
2. Given identical plaintext uploads, When checking the database, Then the stored `encryption_nonce` MUST be cryptographically unique per file.
3. Given an attempt to decrypt evidence, When the user supplies the correct GCM authentication tag, Then the `INTEGRITY_STATUS` equals VERIFIED. 
4. Given an attacker alters 1 byte on disk, When decrypting, Then the `cryptography.exceptions.InvalidTag` MUST be thrown, blocking read.
