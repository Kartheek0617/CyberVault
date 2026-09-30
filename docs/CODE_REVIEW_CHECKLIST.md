# Code Review Checklist (Security Focused)

## Core Security Rules for merging to main:

- [ ] **Authentication:** Are all sensitive endpoints protected using JWT (`get_current_user`) dependency?
- [ ] **Authorization (BOLA/IDOR):** Does the endpoint verify ownership context before fetching data (e.g., using `verify_case_access`)?
- [ ] **Input Validation:** Are inputs parsed entirely by Pydantic schemas before reaching business logic?
- [ ] **Cryptography Constraints:** Does encryption properly append and parse the nonce and authentication tag?
- [ ] **Secrets Management:** Are there any hardcoded keys, tokens, or passwords? (MUST BE ABSENT).
- [ ] **Error Handling:** Are exceptions safely caught without leaking stack traces or internal SQL schemas to HTTP responses?
- [ ] **Audit Trail:** If the logic modifies state, is an explicit call to `audit_service.log_event()` included?
- [ ] **Dependencies:** Are third-party dependencies strictly pinned, minimizing supply chain vulnerabilities?
