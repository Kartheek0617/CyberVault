# CyberVault Target Environment Hardening

## Application Level (FastAPI)
- **Disable Production Debug Mode:** `DEBUG=False` halts detailed stack traces and disables Swagger UI (`/docs`).
- **Restrict CORS:** Explicit origins defined in `ALLOWED_ORIGINS` to prevent arbitrary client access.
- **Secure HTTP Headers:** `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, and strict Content-Security-Policy (CSP) implemented via middleware.
- **Data Minimization / Exception Handling:** Global unhandled exception catching ensures server traces (e.g., SQL syntax) are never leaked to the client.

## Infrastructure Level (Docker Container) [IMPLEMENTED]
- **Non-Root Execution:** `cybervault` unprivileged user created in backend Dockerfile.
- **Minimal Image:** Uses `python:3.10-slim` and `nginx:alpine` to eliminate unnecessary binaries and reduce the attack surface.
- **Health Checks:** Native Docker `HEALTHCHECK` bound to `/api/health` to monitor container viability.

## Operations [IMPLEMENTED]
- **Secret Validation:** Boot sequence in `config.py` explicitly strictly checks that `ENCRYPTION_KEY` is present and exactly 32 bytes (AES-256 requirement). Application crashes safely on failure rather than using default keys.
- **Directory Permissions:** `evidence_storage` mapped correctly with restricted user ACLs.
