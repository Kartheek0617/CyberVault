# CyberVault Definition of Done (DoD)

A User Story or Task is evaluated as **DONE** when the following criteria are rigorously verified:

1. **Functional Completion:** All steps and exceptions defined in the Story's Acceptance Criteria are fully implemented.
2. **Security Controls:** Identified STRIDE mitigations correspond strictly to the codebase logic.
3. **Unit & Integration Testing:** All functional edges are verified.
4. **Security Testing (TDD/CI):** Comprehensive security tests (`test_security_comprehensive.py`) execute successfully in the CI environment (`security-tests.yml`). *(Current baseline: 31 passed).*
5. **Code Quality:** Free of plaintext secrets, logic conforms to the repository style guidelines.
6. **Threat Model Update:** No unmapped architectural boundaries exist.
7. **Requirements Traceability:** Fully mapped in RTM matrix.
8. **Documentation:** API Swagger docs, USE_CASES.md, and diagrams accurately reflect the new system state.
9. **Container Validation:** `docker compose build` succeeds locally.
10. **CI Validation:** Workflows run green.
11. **SonarQube Validation:** (If configured) passes Quality Gates.
12. **Review & Sign-Off:** Pull Request approved by at least one other lead or administrator.
