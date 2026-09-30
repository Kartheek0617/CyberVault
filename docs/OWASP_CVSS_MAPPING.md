# CyberVault OWASP & CVSS Vulnerability Mapping

This document maps identified potential threats (from the STRIDE matrix) against the OWASP Top 10 categories, distinguishing between generic theoretical threats and verified vulnerabilities.

## 1. OWASP Target Classifications

| Threat Area | OWASP 2021 Mapping | Theoretical Vulnerability Scenario | Existing Control in CyberVault | Residual Risk |
|---|---|---|---|---|
| Authorization / IDOR | A01: Broken Access Control | BOLA manipulation on Case APIs | Validated bounds in FastAPI Depends hook ensuring User-to-Case link. | Low |
| Cryptographic Protection | A02: Cryptographic Failures | Hardcoded symmetric keys or downgraded ciphers | strict `ENCRYPTION_KEY` via Environment `.env`. AES-256-GCM enforced. | Low |
| Input Validation | A03: Injection | Malware bypass via MIME spoofing or path traversal | `secure_filename` logic. Strict header typing. | Low |
| Component Alignment | A06: Vulnerable and Outdated Comp. | API dependencies harbor known CVEs | Dependabot workflow tracking. Python 3.10-slim minimal containers. | Medium |
| Application Secrets | A05: Security Misconfiguration | Unintended exposure of stack traces to client | App-level Exception handling capturing full context, emitting generic 500s. | Low |
| Non-repudiation | A08: Software and Data Integrity Failures | Attackers rewrite historical log states | Chain algorithm using `prev_hash` combined with payload data. | Low |
| Telemetry | A09: Security Logging and Monitoring | Attackers exploit lacking observability | Internal `AuditLog` captures granular actions based on JWT. | Medium (Lacks external SIEM) |

---

## 2. Hypothetical CVSS Scoring (For Demonstrated Lab Vulnerabilities)

*Note: The following represents CVSS v3.1 scoring if the **Existing Mitigations** were hypothetically removed/bypassed (e.g. earlier unpatched sprints).*

### 2.1 BOLA / IDOR on Evidence Access (Hypothetical)
- **Vulnerability:** An authenticated user alters the `evidence_id` in the GET request to a file outside their assigned case context.
- **CVSS v3.1 Vector:** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`
- **Base Score:** 6.5 (Medium)
- **Actual CyberVault State:** MITIGATED (`test_authz_idor_bola` passes).

### 2.2 Unrestricted File Upload (Hypothetical)
- **Vulnerability:** Web service accepts non-sanitized `../../` sequence leading to relative path arbitrary overwrite on the OS.
- **CVSS v3.1 Vector:** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`
- **Base Score:** 9.9 (Critical)
- **Actual CyberVault State:** MITIGATED (`test_file_filename_traversal` passes).

### 2.3 Broken Audit Cryptography (Hypothetical)
- **Vulnerability:** Logs write without appending cryptographic linkages, allowing a malicious database admin to selectively DELETE rows unnoticed.
- **CVSS v3.1 Vector:** `CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N`
- **Base Score:** 4.4 (Medium - due to High privileges required off-app).
- **Actual CyberVault State:** MITIGATED (`test_audit_historical_modification` passes).
