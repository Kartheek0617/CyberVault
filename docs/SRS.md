# CyberVault Software Requirements Specification (SRS)

## 1. Introduction
This Software Requirements Specification (SRS) documents the functional and non-functional requirements for the CyberVault Secure Digital Evidence Management System.

## 2. Purpose
The purpose of this document is to clearly define the system boundaries, user interactions, and core components of CyberVault, guiding the secure software engineering lifecycle and serving as a baseline for testing and verification.

## 3. Scope
CyberVault facilitates secure evidence ingestion, cryptographic storage (AES-256-GCM), integrity validation (SHA-256), chain of custody tracking, and final digital report generation (Ed25519) for Law Enforcement and Incident Response teams. 

## 4. Definitions and Abbreviations
- **AES-GCM:** Advanced Encryption Standard - Galois/Counter Mode.
- **RBAC:** Role-Based Access Control.
- **IDOR:** Insecure Direct Object Reference.
- **BOLA:** Broken Object Level Authorization.

## 5. References
- IEEE Std 29148-2018
- OWASP Top 10 (2021)

## 6. Overall Description
CyberVault manages the end-to-end lifecycle of sensitive digital assets. It operates under zero-trust assumptions concerning the storage disk, trusting only in-memory process logic backed by strong deterministic cryptography.

## 7. Product Perspective
The product is a decentralized containerized API application (FastAPI) paired with a React frontend, leveraging an internal SQLite metadata database.

## 8. Product Functions
Authentication, Case Management, Evidence Upload & Validation, Cryptographic Storage, Custody Transferring, Audit Logging, Report Signing.

## 9. User Classes
- **Administrator:** Highest privilege. Manages accounts and cases.
- **Investigator:** Reads/Writes to assigned cases.
- **Evidence Custodian:** Facilitates chain-of-custody handovers.
- **Auditor:** Read-only access to verify hashes.

## 10. Operating Environment
Docker-based environments. Python 3.10, Nginx (Alpine), SQLite.

## 11. Constraints
Mandatory avoidance of database reliance for evidence binary storage to prevent bloat. All files must be file-system stored but heavily encrypted.

## 12. Assumptions and Dependencies
Assumes host providing `.env` is strongly physically secured. Dependency on `argon2-cffi` and `cryptography` modules.

## 13. Functional Requirements
- **FR-01:** System shall authenticate users and issue JWTs.
- **FR-02:** System shall enforce RBAC for all functions.
- **FR-03:** System shall permit valid file uploads strictly bound by MIME and size constraints.
- **FR-04:** System shall securely log all transfers of evidence.
- **FR-05:** System shall generate verifiable JSON-based reports.

## 14. Non-Functional Requirements
- **NFR-01:** System shall restrict storage of encryption keys to memory via Environment variables.
- **NFR-02:** API shall enforce strict rate limits on authentication endpoints.

## 15. External Interface Requirements
The API provides standard HTTP/REST patterns for the React frontend, strictly receiving payloads formatted in JSON or multipart binary.

## 16. Data Requirements
A relational schema modeling Users, Cases, Evidence (metadata), Custody, Audits, and Signatures securely. (See DATA_MODEL.md).

## 17. Use Cases
Refer to `docs/USE_CASES.md`.

## 18. Security Requirements
- **SEC-01:** All evidence must be encrypted via AES-256-GCM.
- **SEC-02:** Evidence integrity verified via GCM Auth Tag on read.
- **SEC-03:** System must block IDOR/BOLA manipulation attempts between Case partitions.
- **SEC-04:** Audit Logs must be hash-chained preventing deletion.

## 19. Risk Analysis
(See THREAT_MODEL.md and THREAT_MATRIX.md).

## 20. Acceptance Criteria
All security tests (`test_security_comprehensive.py`) must pass (GREEN status).

## 21. Requirements Traceability Matrix
Refer to `docs/REQUIREMENTS_TRACEABILITY.md`.

## 22. Revision History
- **v1.0** — Initial creation for Phase 2 Secure Documentation Audit.
