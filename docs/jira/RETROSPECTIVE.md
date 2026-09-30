# CyberVault Sprint Retrospective

*This is a Jira-ready project artifact.*

## Sprint: 2 - Evidence & Validation

### What Went Well
- **TDD Integration:** Writing pure security tests (`test_file_invalid_extension`) prior to implementation saved significant debugging time. The red-green-refactor cycle confirmed we met STRIDE mitigations precisely.
- **Architecture Validation:** FastAPI's dependency injection (`Depends(require_role)`) proved deeply effective at stripping JWT payloads before hitting business logic.

### What Could Be Improved
- **Dependency Scope:** AES-256-GCM configurations were slightly complex, requiring a minor defect carry-over of 3 story points when the `ENCRYPTION_KEY` originally defaulted to an unsafe string during early tests. 
- **Documentation Drift:** DFD and ER diagrams fell behind the actual DB model. 

### Action Items & Process Adjustments
1. Do not push any database migration without updating PUML models simultaneously.
2. Force the application to outright crash on start `AssertionError` if `.env` does not supply exactly 32-bytes for cryptographic keys, preventing silent fallbacks.
