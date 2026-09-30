# CyberVault User Stories

*This is a Jira-ready project artifact.*

| ID | Formatted Story | Priority | Epic Link | Story Points | Assignee | Status |
|---|---|---|---|---|---|---|
| CV-11 | As an admin, I want to manage users and roles, so that I can enforce strict RBAC bounds. | High | EPIC-1 | 5 | Dev_Admin | Done |
| CV-12 | As any user, I want to authenticate via an endpoint, so that I receive a secure JSON Web Token for API access. | Critical | EPIC-1 | 3 | Dev_Core | Done |
| CV-13 | As an administrator, I want to provision Cases and bind investigators, so that unauthorized personnel cannot view case artifacts. | High | EPIC-2 | 5 | Dev_Admin | Done |
| CV-14 | As an investigator, I want my uploaded file metadata validated, so that malicious extensions and MIME spoofing attempts fail immediately. | Critical| EPIC-3 | 3 | Dev_Core | Done |
| CV-15 | As a custodian, I want uploaded evidence forcibly encrypted via AES-256-GCM, so that data at rest is fundamentally immune to theft. | Critical | EPIC-4 | 13 | Crypto_Eng | Done |
| CV-16 | As an auditor, I want all DB actions appended to a cryptographic hash-chain, so that destructive tampering is provable. | High | EPIC-5 | 8 | Crypto_Eng | Done |
| CV-17 | As a user, I want to transfer custody of digital assets, so that handovers are definitively logged in the ledger. | Medium | EPIC-5 | 5 | Dev_Core | Done |
| CV-18 | As an investigator, I want finalizing reports digitally signed with Ed25519, so that they cannot be repudiated. | Medium | EPIC-6 | 5 | Crypto_Eng | Done |
