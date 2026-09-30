"""
CyberVault — Secure Digital Evidence Management System
Core application settings loaded from environment variables.
"""
import base64
import secrets
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./cybervault.db"

    # ── Application Security ──────────────────────────────────────────────────
    SECRET_KEY: str = secrets.token_hex(64)

    # ── JWT ───────────────────────────────────────────────────────────────────
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # ── Evidence Encryption (AES-256-GCM) ────────────────────────────────────
    ENCRYPTION_KEY: str = ""  # base64 of 32 bytes

    # ── Digital Signatures (Ed25519) ──────────────────────────────────────────
    SIGNING_PRIVATE_KEY_B64: str = ""
    SIGNING_PUBLIC_KEY_B64: str = ""

    # ── Storage ───────────────────────────────────────────────────────────────
    EVIDENCE_STORAGE_PATH: str = "./evidence_storage"

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    LOGIN_RATE_LIMIT_MAX: int = 5
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = 300

    # ── Environment ───────────────────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key(cls, v: str, info) -> str:
        if not v:
            raise ValueError(
                "ENCRYPTION_KEY is missing! You must configure a fixed, persistent ENCRYPTION_KEY "
                "in the .env file for AES-256-GCM. Do not use dynamic/random keys across restarts."
            )
        try:
            key_bytes = base64.b64decode(v)
            if len(key_bytes) != 32:
                raise ValueError(f"ENCRYPTION_KEY must be exactly 32 bytes (256 bits). Found {len(key_bytes)} bytes.")
        except Exception as e:
            if isinstance(e, ValueError) and "ENCRYPTION_KEY" in str(e):
                raise
            raise ValueError("ENCRYPTION_KEY must be a valid base64-encoded string.")
        return v

    @field_validator("DEBUG", mode="before")
    @classmethod
    def validate_debug_mode(cls, v, info) -> bool:
        env = info.data.get("ENVIRONMENT", "development").lower()
        if env == "production" and v in [True, "true", "True", "1"]:
            raise ValueError("CRITICAL SECURITY ERROR: DEBUG mode cannot be enabled in 'production' environment.")
        # pydantic converts standard types, just return the raw boolean evaluation if we don't raise
        return str(v).lower() in ("true", "1", "yes")

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    @property
    def evidence_storage_path(self) -> Path:
        p = Path(self.EVIDENCE_STORAGE_PATH)
        p.mkdir(parents=True, exist_ok=True)
        return p

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
