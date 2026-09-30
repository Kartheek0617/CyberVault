# CyberVault Academic Review & Demonstration Guide

This document systematically walks through how CyberVault satisfies Secure Software Engineering (SSE) and Agile requirements.

## 1. Project Overview & Problem Statement
*   **WHAT IT IS:** CyberVault is an advanced Secure Digital Evidence Management System (SDEMS).
*   **HOW WE USE IT:** Addresses stringent requirements for the forensic evidence lifecycle (Confidentiality, Integrity, Non-Repudiation, Chain of Custody).
*   **WHERE IT EXISTS:** Application configuration (`backend/app`).
*   **HOW TO DEMONSTRATE IT:** Boot the system (`docker compose up`) and upload a file. The binary will instantly be ciphertext-encrypted.

## 2. Requirements & Use Cases
*   **WHAT IT IS:** Software Requirements Specifications covering functionalities & boundaries.
*   **HOW WE USE IT:** Defined actors (Admin, Investigator, Auditor) with specific operational flows.
*   **WHERE IT EXISTS:** `docs/REQUIREMENTS.md` and `docs/USE_CASES.md`.
*   **EXPECTED RESULT:** Functional matching of the Markdown use cases with the React frontend interfaces.

## 3. Architecture & Threat Model
*   **WHAT IT IS:** Formal network boundaries and STRIDE vulnerability modeling.
*   **HOW WE USE IT:** Analyzes potential breaches (e.g. JWT spoofing, Storage tampering) and defines mitigations.
*   **WHERE IT EXISTS:** `docs/SECURITY_ARCHITECTURE.md` and `docs/THREAT_MODEL.md`.
*   **EXPECTED RESULT:** Clear separation of FastAPI processing boundaries vs SQLite storage interfaces.

## 4. Environment Hardening & Containerization
*   **WHAT IT IS:** Converting local Dev environments into locked down immutable Production hosts.
*   **HOW WE USE IT:** Using `.dockerignore` to prevent `.env` leaks, minimizing root privileges, and omitting Swagger/debug traces.
*   **WHERE IT EXISTS:** `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`.
*   **HOW TO DEMONSTRATE IT:** Build containers and execute without a `.env` ENCRYPTION_KEY -> Engine will firmly crash (Secure Failure).

## 5. Security Testing, TDD & CI
*   **WHAT IT IS:** Test-Driven Development (TDD) incorporated with Continuous Integration.
*   **HOW WE USE IT:** We defined our fail-states (RED) for security anomalies (Invalid JWT, Invalid File, Tampered Crypto), developed the logic (GREEN), and pushed to an automated pipeline.
*   **WHERE IT EXISTS:** `backend/tests/test_security_comprehensive.py` and `.github/workflows/security-tests.yml`.
*   **HOW TO DEMONSTRATE:** Run `pytest backend/tests/test_security_comprehensive.py` to see assertions match.

## 6. Security Economics & GRC
*   **WHAT IT IS:** Governance, Risk, and Compliance overlaid onto developmental cost constraints.
*   **HOW WE USE IT:** Measuring the catastrophic cost of an evidence leak against the minimal computational cost of AES-GCM integration.
*   **WHERE IT EXISTS:** `docs/SECURITY_ECONOMICS.md` and `docs/GRC_MATRIX.md`.
*   **EXPECTED RESULT:** Academic evaluation of mitigative ROIs.

## 7. Agile Methodology & Code Review
*   **WHAT IT IS:** Using Sprints, Backlogs, WIP limits, and checklists to consistently iterate while retaining security boundaries.
*   **HOW WE USE IT:** WIP Limits (Max 3) ensure context-switching doesn't lead to unfinished security patches. Code Review checks force authentication wrappers to be validated prior to merge.
*   **WHERE IT EXISTS:** `docs/AGILE_PROCESS.md` and `docs/CODE_REVIEW_CHECKLIST.md`.
*   **HOW TO DEMONSTRATE:** Review Sprint metrics in the Agile markdown.

---

## COURSE COVERAGE MATRIX (Final Summary)

| Topic | Implemented | Documentation | Test/Evidence | Demonstration Location |
|---|---|---|---|---|
| **Software Process Models** | Yes | `AGILE_PROCESS.md` | Sprint Backlog | `AGILE_PROCESS.md` Sec 2 |
| **Requirements Engineering**| Yes | `REQUIREMENTS.md` | Functional Traces | `REQUIREMENTS_TRACEABILITY.md` |
| **Vulnerability Analysis** | Yes | `VULNERABILITY_ASSESSMENT.md` | IDOR Protections | `TC-AUTHZ-02` |
| **Threat Modeling** | Yes | `THREAT_MODEL.md` | STRIDE Matrix | `THREAT_MODEL.md` Sec 1-6 |
| **Secure Architecture** | Yes | `SECURITY_ARCHITECTURE.md` | Trust Boundaries | `SECURITY_ARCHITECTURE.md` |
| **Code Review / TDD** | Yes | `CODE_REVIEW_CHECKLIST.md` | PyTest Suite | `backend/tests/` |
| **Target Hardening** | Yes | `SECURITY_HARDENING.md` | Config Validators | `backend/app/core/config.py` |
| **Secure Deployment** | Yes | `SECURITY_DEPLOYMENT.md` | Dockerized Flow | `docker-compose.yml` |
| **Containerization** | Yes | - | Dockerfiles | `backend/Dockerfile` & `frontend/` |
| **Security Testing / CI** | Yes | `SECURITY_TESTING.md` | GitHub Actions | `.github/workflows/` |
| **Economics / Cost** | Yes | `SECURITY_ECONOMICS.md` | Cost vs Breach | `SECURITY_ECONOMICS.md` |
| **GRC** | Yes | `GRC_MATRIX.md` | Risk Matrices | `GRC_MATRIX.md` |
