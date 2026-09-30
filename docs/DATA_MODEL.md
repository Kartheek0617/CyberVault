# CyberVault Data Model (ER Diagram)

This document describes the core entities in the CyberVault Secure Digital Evidence Management System. The data model is designed to enforce referential integrity, securely store cryptographic evidence metadata, and maintain immutable audit and custody chains.

## 1. Entities & Purpose

- **User**: Represents system users (Administrators, Investigators, Evidence Custodians, Auditors). Contains Bcrypt password hashes and RBAC profiles.
- **Case**: The primary investigative container. Groups evidence and controls access boundaries.
- **CaseMember**: Junction table managing access control lists (ACL) for which Users have access to which Cases.
- **Evidence**: Stores metadata about uploaded digital evidence. Includes SHA-256 hashes, AES-256-GCM nonces, UUIDs, and paths to the ciphertext but *never* the encryption key itself.
- **ChainOfCustody**: Immutable ledger recording the physical/digital transfer of evidence. Each event is cryptographically hash-chained.
- **AuditLog**: Maintains a tamper-evident, monotonically increasing, hash-chained system action logger for compliance.
- **Report**: Represents a finalized, digitally signed summary of case evidence. 
- **DigitalSignature**: Stores the Ed25519 cryptographic signature and associated public keys asserting the authority of a generated Report.
- **SecurityEvent**: Logs specific security anomalies (failed logins, integrity check failures, IDOR attempts) into a triage dashboard for auditors.

## 2. Relationships

- **User - Case**: 1-to-Many (A User creates many Cases).
- **User - CaseMember - Case**: Many-to-Many (Users can be granted access to Many cases; Cases have Many members).
- **Case - Evidence**: 1-to-Many (A Case contains many items of Evidence).
- **Evidence - ChainOfCustody**: 1-to-Many (An Evidence item has many historical custody events).
- **Case - Report**: 1-to-Many (A Case can produce multiple finalized reports).
- **Report - DigitalSignature**: 1-to-1 (Each report carries exactly one authoritative signature).
