# CyberVault Use Cases

## Overview
This document specifies the primary Use Cases supported by the CyberVault application, based securely on current functionalities and database models.

## Actors
- **Administrator:** Can manage users, create cases, and assign members to cases.
- **Investigator:** Law enforcement officer capable of accessing assigned cases, uploading evidence, and generating reports.
- **Evidence Custodian:** Staff strictly responsible for the receipt, transfer, and archival of evidence items.
- **Auditor:** Security/Compliance officer who verifies audit chains, reports, and evidence integrity.

---

## UC-01: Login
- **Actor:** Any User
- **Goal:** Authenticate to the system.
- **Preconditions:** User exists and is not locked.
- **Main Flow:** 
  1. User enters username and password.
  2. Backend validates Bcrypt password hash.
  3. Backend generates short-lived JWT (HS256).
- **Security Controls:** Rate limiting, strong cryptographic hash matching.
- **Acceptance Criteria:** Successful login returns HTTP 200 with JWT; incorrect returns HTTP 401.

## UC-02: Manage Users
- **Actor:** Administrator
- **Goal:** Provision and manage identities securely.
- **Main Flow:** Admin adds user details, assigns role (`ADMIN`, `INVESTIGATOR`, `EVIDENCE_CUSTODIAN`, `AUDITOR`).
- **Security Controls:** JWT RBAC check on `/api/users`.

## UC-03: Manage Cases
- **Actor:** Administrator
- **Goal:** Create case containers and bind authorized investigators via ACL.
- **Main Flow:** Admin specifies case parameters, assigns investigators to `CaseMember` table.
- **Postconditions:** Case is strictly accessible only to assigned members.

## UC-04: Upload Evidence
- **Actor:** Investigator / Evidence Custodian
- **Goal:** Securely attach digital evidence to an existing case.
- **Preconditions:** Actor assigned to case.
- **Main Flow:** 
  1. File is passed. Validation drops extreme filesizes and illegal extensions.
  2. System computes pre-encryption SHA-256 for originality.
  3. System encrypts file securely using AES-256-GCM.
  4. Encrypted file is written to `./evidence_storage`. Database is updated.
- **Security Controls:** IDOR/BOLA protection, AES-256-GCM, Path Traversal protections.

## UC-05: Verify Evidence Integrity
- **Actor:** Auditor / Investigator
- **Goal:** Prove the encrypted evidence has not suffered tampering on disk.
- **Main Flow:** Decrypt stream utilizing GCM Auth Tag. Calculate SHA-256 and confirm match against the database. 
- **Exception Flow:** Returns `INTEGRITY_FAILURE` event if GCM tag fails or hashes do not align.

## UC-06: Transfer Evidence Custody
- **Actor:** Investigator / Evidence Custodian
- **Goal:** Record a formal change in custody.
- **Main Flow:** Actor initiates transfer logic to new Custodian UUID. System creates a `ChainOfCustody` record linked cryptographically to the previous event lock.

## UC-07: Receive Evidence
- **Actor:** Investigator / Evidence Custodian
- **Goal:** Acknowledge receipt of a transferred asset, completing the handover.
- **Main Flow:** Changes status to `ACTIVE` and `current_custodian` to Actor. Logs to `ChainOfCustody`.

## UC-08: View Chain of Custody
- **Actor:** Auditor
- **Goal:** Observe the full history of interactions for a specific digital asset.
- **Main Flow:** API returns ordered list from `ChainOfCustody` table for the target Evidence.

## UC-09: View Audit Logs
- **Actor:** Auditor
- **Goal:** Read system-wide actions for compliance or incident response.
- **Main Flow:** Retrieve hash-chained elements from `AuditLog`. Auditor can trigger verification to spot hidden omissions.

## UC-10: Generate Report
- **Actor:** Investigator / Administrator
- **Goal:** Compile case materials into a concise layout.
- **Main Flow:** System gathers Case details, Evidence metadata, and generates a JSON payload/record.

## UC-11: Sign Report
- **Actor:** Investigator / Administrator
- **Goal:** Guarantee the report originated from the actor and prevent repudiation.
- **Main Flow:** System locks the Report payload, calculates signature using Ed25519 keypair, stores result in `DigitalSignature`.

## UC-12: Verify Report Signature
- **Actor:** Auditor / Administrator
- **Goal:** Verify authenticity of a previously generated report.
- **Main Flow:** Extract Report payload and signature. Execute Ed25519 cryptographic check.
