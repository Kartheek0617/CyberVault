# CyberVault Requirements Specification

## 1. Problem Statement
Managing digital evidence securely is a complex cryptographic and logistical challenge. Chain of Custody must be verifiably maintained, evidence tampering must be reliably detected, and access must be stringently controlled to prevent unauthorized disclosures or malicious repudiation. 

## 2. Stakeholders
- **Investigators/Law Enforcement Officers (LEOs):** Primary uploaders and consumers of case evidence.
- **Auditors:** Security personnel responsible for verifying operations without modifying them.
- **Administrators (SysAdmins):** Manage users, assign cases, and maintain infrastructure.
- **Evidence Custodians:** Handle technical custody transfers between departments.

## 3. System Scope
CyberVault is a web-centric Secure Digital Evidence Management System (SDEMS). It covers secure ingestion, encrypted at-rest storage (AES-256-GCM), integrity monitoring via SHA-256 and authenticated hash chains, access control through Role-Based Access Control (RBAC), and Ed25519-signed final reporting. 

## 4. Functional Requirements
- **FR-1:** The system shall authenticate users via JWT.
- **FR-2:** The system shall enable administrators to create cases and assign members.
- **FR-3:** The system shall allow authorized case members to upload digital evidence.
- **FR-4:** The system shall encrypt all uploaded evidence using AES-256-GCM before filesystem storage.
- **FR-5:** The system shall generate SHA-256 hashes for all evidence upon upload.
- **FR-6:** The system shall record and enforce a continuous chain of custody.
- **FR-7:** The system shall produce Ed25519 digitally signed investigative reports.

## 5. Non-Functional Requirements
- **NFR-1 (Security):** All encryption keys must be managed outside source and version control (e.g., via strictly permissioned `.env`).
- **NFR-2 (Performance):** The system shall handle file uploads up to 50MB per file in under 30 seconds.
- **NFR-3 (Availability):** Health checks shall verify endpoint availability.

## 6. Security Requirements
- **SR-1:** Enforce Least Privilege via strict RBAC.
- **SR-2:** Evidence cryptographic keys must be persistent and not dynamically regenerated upon server restart.
- **SR-3:** Audit logs must be hash-chained to detect historical tampering.
- **SR-4:** All API endpoints must protect against IDOR/BOLA by confirming case access boundaries.

## 7. Assumptions, Constraints, & Risks
- **Constraint:** Application must run containerized using Nginx and Python base images.
- **Assumption:** Host system operating environment is physically and logically secured.
- **Risk:** Compromise of `ENCRYPTION_KEY` exposes all ciphertext. (Mitigated via strict `.env` governance).
