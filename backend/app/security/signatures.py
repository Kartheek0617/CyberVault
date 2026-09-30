"""
CyberVault — Ed25519 digital signatures for evidence reports.
Security:
  - Ed25519 provides strong, fast digital signatures.
  - Private key is NEVER exposed to the frontend or included in responses.
  - Public key is available for verification.
  - Keys loaded from environment variables.
  - Auto-generates a key pair on first run if not configured (development).
"""
import base64
import hashlib
import os

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from app.core.config import get_settings

# ─────────────────────────────────────────────────────────────────────────────
# Key loading (lazy, cached per process)
# ─────────────────────────────────────────────────────────────────────────────

_private_key: Ed25519PrivateKey | None = None
_public_key: Ed25519PublicKey | None = None


def _load_keys():
    global _private_key, _public_key
    if _private_key is not None:
        return

    settings = get_settings()

    if settings.SIGNING_PRIVATE_KEY_B64 and settings.SIGNING_PRIVATE_KEY_B64 != "CHANGE_ME_base64_encoded_ed25519_private_key":
        raw = base64.b64decode(settings.SIGNING_PRIVATE_KEY_B64)
        _private_key = Ed25519PrivateKey.from_private_bytes(raw)
        _public_key = _private_key.public_key()
    else:
        # Auto-generate for development; warn loudly
        print(
            "[WARNING] No SIGNING_PRIVATE_KEY_B64 configured. "
            "Generating ephemeral Ed25519 key pair — signatures will NOT persist across restarts. "
            "Set SIGNING_PRIVATE_KEY_B64 and SIGNING_PUBLIC_KEY_B64 in .env for production."
        )
        _private_key = Ed25519PrivateKey.generate()
        _public_key = _private_key.public_key()


def sign_data(data: bytes) -> tuple[str, str, str]:
    """
    Sign data with the Ed25519 private key.

    Returns:
        (signature_hex, public_key_hex, data_hash_hex)

    data_hash_hex is SHA-256 of the data, used for verification records.
    """
    _load_keys()
    data_hash = hashlib.sha256(data).hexdigest()
    signature = _private_key.sign(data)
    pub_bytes = _public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    return signature.hex(), pub_bytes.hex(), data_hash


def verify_signature(data: bytes, signature_hex: str, public_key_hex: str) -> bool:
    """
    Verify an Ed25519 signature.
    Returns True if valid, False if invalid or tampered.
    Never raises to callers.
    """
    try:
        pub_bytes = bytes.fromhex(public_key_hex)
        pub_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
        signature = bytes.fromhex(signature_hex)
        pub_key.verify(signature, data)
        return True
    except (InvalidSignature, ValueError, Exception):
        return False


def get_public_key_hex() -> str:
    """Return the current public key as hex (safe to expose)."""
    _load_keys()
    pub_bytes = _public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    return pub_bytes.hex()
