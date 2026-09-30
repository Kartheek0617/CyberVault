# CyberVault - Course Compliance Matrix (Phase 3 Updated)

| Requirement | Lab/CO Source | Current Status | Evidence | Gap / Phase 3 Result | Action Required |
|---|---|---|---|---|---|
| 1. Containers | Course | YELLOW | `Dockerfile`, `.dockerignore` | **EXECUTION BLOCKED** - Engine unavailable | Requires Docker Install |
| 2. Docker Compose | Course | YELLOW | `docker-compose.yml` | **EXECUTION BLOCKED** | Requires Docker Install |
| 3. CI | Course | GREEN | `ci.yml`, `security-tests.yml` | Workflows configured and verified locally | None |
| 4. CD | Course | YELLOW | `cd.yml` | **EXECUTION BLOCKED** - No target server | Deploy to AWS/Azure |
| 5. SRS | Lab | GREEN | `docs/SRS.md` | Documented per IEEE 29148 | None |
| 6. Jira | Lab | YELLOW | `docs/jira/` | Artifacts produced, awaiting actual Jira push| Upload to Jira Software |
| 7. Product Backlog | Lab | GREEN | `docs/jira/PRODUCT_BACKLOG.md` | Documented | None |
| 8. User Stories | Lab | GREEN | `docs/jira/USER_STORIES.md` | Documented | None |
| 9. Epics | Lab | GREEN | `docs/jira/EPICS.md` | Documented | None |
| 10. Story Points | Lab | GREEN | `docs/jira/USER_STORIES.md` | Documented | None |
| 11. Sprint Backlog | Lab | GREEN | `docs/jira/SPRINT_BACKLOG.md` | Documented | None |
| 12. Sprint Goals | Lab | GREEN | `docs/jira/SPRINT_PLAN.md` | Documented | None |
| 13. Sprint Review | Lab | GREEN | `docs/jira/SPRINT_REVIEW.md` | Documented | None |
| 14. Sprint Retrospective | Lab | GREEN | `docs/jira/RETROSPECTIVE.md` | Documented | None |
| 15. Burndown | Lab | GREEN | `docs/AGILE_PROCESS.md` | Documented mathematically | None |
| 16. Velocity | Lab | GREEN | `docs/AGILE_PROCESS.md` | Documented (11.75 pts) | None |
| 17. Defect Carry-over| Lab | GREEN | `docs/jira/RETROSPECTIVE.md`| Documented | None |
| 18. Kanban | Lab | GREEN | `docs/AGILE_PROCESS.md` | Documented | None |
| 19. WIP | Lab | GREEN | `docs/AGILE_PROCESS.md` | Limit documented (3 items) | None |
| 20. DFD | Lab | GREEN | `docs/DFD.md`, `.puml` | Documented with boundaries | None |
| 21. Use Case Diagram | Lab | GREEN | `docs/USE_CASES.md`, `.puml` | Documented | None |
| 22. ER/Data Model | Lab | GREEN | `docs/DATA_MODEL.md`, `.puml` | Matched exactly against SQLAlchemy models | None |
| 23. STRIDE | Lab | GREEN | `docs/THREAT_MATRIX.md` | Exact mitigations traced to Pytest | None |
| 24. ASTRIDE | Lab | GRAY | `docs/THREAT_MODEL.md` | Not Applicable (No AI Agent) | None |
| 25. CVSS | Lab | GREEN | `OWASP_CVSS_MAPPING.md` | Theoretical mapped | None |
| 26. OWASP mapping | Lab | GREEN | `OWASP_CVSS_MAPPING.md` | Documented | None |
| 27. SonarQube Setup| Lab | YELLOW | `sonar-project.properties` | **EXECUTION BLOCKED** - Scanner unavailable | Install SonarScanner |
| 28. Static Analysis | Lab | YELLOW | `docs/SONARQUBE.md` | **EXECUTION BLOCKED** | Execute SonarScanner |
| 29. Security testing | Lab | GREEN | Pytest Logs | 31/31 EXECUTED, VERIFIED | None |
| 30. CI security tests| Lab | GREEN | `security-tests.yml` | CONFIGURED | None |
| 31. Threat mitigation| Lab | GREEN | `THREAT_MATRIX.md` | Traced and proven in code | None |
| 32. Requirements trace| Lab| GREEN | `REQUIREMENTS_TRACEABILITY.md`| Mapped completely to Pytest | None |
| 33. Security arch | Lab | GREEN | `SECURITY_ARCHITECTURE.md` | Documented | None |
| 34. Secure deployment| Lab | YELLOW | `SECURITY_DEPLOYMENT.md` | Deployment blocked by environment | Provision VM |
| 35. Hardening | Lab | GREEN | `SECURITY_HARDENING.md` | Docker constraints reviewed and added | None |
| 36. Security economy | Lab | GREEN | `SECURITY_ECONOMICS.md` | Implemented proactive vs reactive contrast| None |
| 37. GRC | Lab | GREEN | `GRC_MATRIX.md` | Documented | None |
| 38. Definition of Done| Lab | GREEN | `DEFINITION_OF_DONE.md` | Standardized | None |
