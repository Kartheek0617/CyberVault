"""
CyberVault — AES-256-GCM evidence encryption/decryption.
Security:
  - Uses authenticated encryption (AES-GCM) so tampering with ciphertext is detectable.
  - Each file uses a unique random 96-bit nonce (12 bytes, as recommended for GCM).
  - Encryption key loaded from environment variable, never hard-coded.
  - Nonce is stored in DB (not in the file), separate from ciphertext.
"""
import base64
import hashlib
import os
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import get_settings


def _get_aes_key() -> bytes:
    """
    Load the AES-256 key from environment settings.
    Key must be base64-encoded 32 bytes.
    Generates a temporary key if not configured (development only).
    """
    settings = get_settings()
    if settings.ENCRYPTION_KEY:
        key = base64.b64decode(settings.ENCRYPTION_KEY)
        if len(key) != 32:
            raise ValueError("ENCRYPTION_KEY must decode to exactly 32 bytes for AES-256.")
        return key
    # Development fallback: derive from SECRET_KEY (NOT for production)
    return hashlib.sha256(settings.SECRET_KEY.encode()).digest()


def encrypt_evidence(plaintext: bytes) -> tuple[bytes, str]:
    """
    Encrypt evidence bytes using AES-256-GCM.

    Returns:
        (ciphertext_with_tag: bytes, nonce_hex: str)

    The GCM authentication tag is appended to ciphertext by the library.
    Store nonce_hex in the database separately.
    """
    key = _get_aes_key()
    nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)  # AAD=None
    return ciphertext, nonce.hex()


def decrypt_evidence(ciphertext: bytes, nonce_hex: str) -> bytes:
    """
    Decrypt evidence bytes using AES-256-GCM.
    Raises an exception if authentication fails (tampered ciphertext).
    """
    key = _get_aes_key()
    nonce = bytes.fromhex(nonce_hex)
    aesgcm = AESGCM(key)
    # Will raise cryptography.exceptions.InvalidTag if tampered
    return aesgcm.decrypt(nonce, ciphertext, None)


def calculate_sha256(data: bytes) -> str:
    """Calculate the SHA-256 hash of raw bytes. Returns hex digest."""
    return hashlib.sha256(data).hexdigest()


def generate_storage_filename(extension: str) -> str:
    """
    Generate a cryptographically random storage filename.
    Never derived from the original filename — prevents path traversal and
    makes storage filenames unpredictable.
    """
    random_name = secrets.token_hex(32)
    safe_ext = extension.lstrip(".").lower()[:10]  # limit extension length
    return f"{random_name}.enc"


def generate_event_hash(previous_hash: str | None, event_data: str) -> str:
    """
    Calculate hash-chain entry: SHA256(previous_hash + event_data).
    Used for tamper-evident audit logs and chain-of-custody records.
    """
    content = (previous_hash or "GENESIS") + event_data
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
