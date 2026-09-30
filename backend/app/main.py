"""
CyberVault — FastAPI Application Entry Point.
Implements security headers, CORS, error handling, and route registration.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, audit, cases, dashboard, evidence, reports, users
from app.core.config import get_settings
from app.core.database import Base, engine

settings = get_settings()

# ── Configure structured logging ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("cybervault")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup: create tables if they don't exist."""
    logger.info("CyberVault starting up...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured.")
    yield
    logger.info("CyberVault shutting down.")


# ── FastAPI App ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CyberVault API",
    description="Secure Digital Evidence Management System",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # Enable standard /docs
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)


# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)


# ── Security Headers Middleware ────────────────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    # CSP: restrict to same origin and required APIs
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    return response


# ── Global Error Handler ───────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Never expose internal stack traces, SQL errors, or filesystem paths.
    Log the real error server-side only.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred. Please contact the system administrator."},
    )


# ── Route Registration ─────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(cases.router)
app.include_router(evidence.router)
app.include_router(audit.router)
app.include_router(reports.router)
app.include_router(dashboard.router)


@app.get("/api/health")
async def health_check_api():
    """Health check endpoint (no auth required)."""
    return {"status": "operational", "system": "CyberVault"}

@app.get("/health")
async def health_check():
    """Root Health check endpoint for ease of use (no auth required)."""
    return {"status": "healthy", "service": "CyberVault"}
