# CyberVault Final Implementation Matrix

| Topic | Actual Tool/System | Implementation | Execution | Evidence |
|------|------|------|------|------|
| Agile | Scrum process | Configured | Blocked (No Jira Access) | Jira mapping exists in docs/jira/ |
| Jira | Jira Cloud | Configured | Blocked (No Connector/Creds) | `docs/evidence/jira` empty (blocked) |
| DoD | Process | Configured | Verified | Implemented via Pytest controls |
| CI | GitHub Actions | Configured | Verified (Local Execution) | `python -m pytest` passes 31/31 locally |
| CD | GitHub Actions | Configured | Blocked (No Prod Server) | `docs/diagrams/cybervault-ci-cd.puml` |
| Docker | Docker Compose | Configured | Blocked (No Docker Engine) | Dockerfiles provided, host lacks CLI |
| SonarQube | SonarQube | Configured | Blocked (No Sonar Scanner) | `sonar-project.properties` provided |
| GRC | Control Registry | Implemented | Verified | `docs/evidence/grc/control_registry.json` |
| Diagrams | PlantUML | Implemented | Executed | `docs/evidence/diagrams/*.png` rendered |
