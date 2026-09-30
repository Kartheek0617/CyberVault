# CyberVault Secure Deployment Guide

## 1. Architecture Boundaries (IMPLEMENTED)
- **Frontend / Presentation Layer:** React SPA compiled statically, served by Nginx (Alpine Container).
- **Backend / Application Layer:** FastAPI application running via Uvicorn (Python Slim Container).
- **Database / Data Tier:** SQLite database (`cybervault.db`) mounted via Docker volumes mapping to host.
- **Evidence Storage:** Physical block storage mapped via Docker volumes for AES-256-GCM ciphertexts.

## 2. Secrets Management
- All keys (`SECRET_KEY`, `ENCRYPTION_KEY`, `SIGNING_PRIVATE_KEY_B64`) MUST be provisioned using environment variables.
- Never hardcode these variables in `.env` files tracked by Git (see `.dockerignore` / `.gitignore`).

## 3. Network Configuration (IMPLEMENTED)
- Backend explicitly binds to port 8000 and restricts CORS to local domains.
- Exposed ports in Docker Compose are explicitly mapped.

## Production CI/CD (REQUIRES CONFIGURATION)
- Deployment to an external cloud platform is currently pending. Local/Host deployments are functional.

## 4. Deployment Validation
Follow these steps to validate deployment integrity:
1. `docker compose build` - Assembles immutable images.
2. `docker compose up -d` - Launches cluster.
3. `curl http://localhost:8000/health` - Check health status.
4. Attempt to hit `/docs`. If `ENVIRONMENT=production`, it MUST yield a 404.
