# CyberVault CI/CD & Security Pipelines

## 1. Branching & Triggers
- **Main Branch:** Protected. Merges require passing CI checks.
- **Dev Branch:** Work-in-progress, triggers CI builds.
- **Pull Requests:** Evaluated by GitHub Actions prior to review.

## 2. Test Gates
Our pipeline implements strict blocking gates:
- **Security Test Gate:** `pytest` must return a 0 exit code (100% pass on all 31 security assertions). If `.env` fallbacks or cryptography rules are violated, the pipeline halts securely.
- **Frontend Build Gate:** Vite compiler errors halt execution.
- **Docker Build Gate:** Verifies `Dockerfile` integrity for both backend and frontend environments upon push.

## 3. SonarQube Integration
- Integrated via `SonarSource/sonarcloud-github-action`.
- Gate currently set to `continue-on-error: true` while waiting for actual credential injection (`SONAR_TOKEN`).
- Requires a functional Quality Gate profile (e.g., standard "Sonar way").

## 4. Secrets Management
- Keys such as `SONAR_TOKEN`, `DEPLOY_KEY`, `PROD_SERVER` are strictly managed via GitHub Actions Secrets.
- Pipeline environment variables for tests use isolated strings (e.g., `ci_secret_key_123_not_used_in_prod`) ensuring production keys never touch VMs.

## 5. Artifact Handling & Failures
- The pipeline immediately halts upon a security regression.
- Currently, NO container artifacts (.tar or pushes to Docker Hub/GHCR) occur passively without signed releases.

## 6. Continuous Deployment
- **Status:** CD EXECUTION REQUIRED. 
- A baseline template (`cd.yml`) exists mapping deployment to `main`, but lacks a reachable hardened server target.
