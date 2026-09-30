# CyberVault Epics

*This is a Jira-ready project artifact.*

## EPIC-1: Authentication & Authorization Foundation
**Description:** Implement robust multi-tiered access control (JWT/HS256) and user definitions (Bcrypt).
**Security Target:** Zero spoofing or unauthorized entry.
**Status:** DONE

## EPIC-2: Case Isolation & Management
**Description:** Create partition boundaries utilizing IDOR/BOLA mitigations to link Users to specific Cases securely.
**Security Target:** Zero horizontal privilege escalation across cases.
**Status:** DONE

## EPIC-3: Evidence Ingestion & Validation
**Description:** API capabilities to accept multipart forms while aggressively dropping arbitrary or malicious payloads.
**Security Target:** Neutralize path traversal and executable injection possibilities.
**Status:** DONE

## EPIC-4: Cryptographic At-Rest Core
**Description:** Force all binary blobs through AES-256-GCM pipelines with strictly bounded memory allocations.
**Security Target:** Confidentiality and Integrity via hardware-grade symmetric cryptography.
**Status:** DONE

## EPIC-5: Immutable Chain of Custody & Audit
**Description:** Build hash-chained sequential ledgers (SHA-256) tracking all read/write/transfer actions server wide.
**Security Target:** Non-repudiation and evident destruction of data logic upon database modification.
**Status:** DONE

## EPIC-6: Non-Repudiable Reporting
**Description:** End-to-end report amalgamation using Asymmetric (Ed25519) keypairs for signing.
**Security Target:** Court-admissible proof of report origin.
**Status:** DONE
