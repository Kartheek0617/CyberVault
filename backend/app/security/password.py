"""
CyberVault — Password hashing using Argon2id via passlib.
Security: Argon2id is the current best-practice password hashing algorithm.
Never store or log plaintext passwords.
"""
from passlib.context import CryptContext

# Argon2id with recommended parameters
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,   # 64 MB
    argon2__time_cost=3,          # 3 iterations
    argon2__parallelism=1,
    argon2__hash_len=32,
    argon2__type="ID",            # Argon2id
)


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id. Never returns the plaintext."""
    return pwd_context.hash(password)


def verify_password(plaintext: str, hashed: str) -> bool:
    """Verify a plaintext password against its Argon2id hash."""
    return pwd_context.verify(plaintext, hashed)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Enforce strong password policy.
    Returns (is_valid, error_message).
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character."
    return True, ""
