import pytest
from app.security.encryption import encrypt_evidence, decrypt_evidence, _get_aes_key, calculate_sha256
from app.core.config import get_settings
from cryptography.exceptions import InvalidTag
import os

def test_encrypt_decrypt_success():
    """1. Encrypt → decrypt with the same persistent key → success."""
    plaintext = b"Test evidence data for AES-GCM"
    ciphertext, nonce = encrypt_evidence(plaintext)
    decrypted = decrypt_evidence(ciphertext, nonce)
    assert decrypted == plaintext

def test_persistent_key_recreation():
    """2. Encrypt → restart/recreate settings → decrypt → success."""
    plaintext = b"Testing persistence"
    ciphertext, nonce = encrypt_evidence(plaintext)
    
    # Simulate a "restart" by explicitly clearing lru_cache of settings
    get_settings.cache_clear()
    
    decrypted = decrypt_evidence(ciphertext, nonce)
    assert decrypted == plaintext
    
def test_modify_ciphertext_fails():
    """3. Modify ciphertext → AES-GCM decryption fails."""
    plaintext = b"Sensitive Data"
    ciphertext, nonce = encrypt_evidence(plaintext)
    
    # Tamper with ciphertext
    tampered_ciphertext = bytearray(ciphertext)
    tampered_ciphertext[0] ^= 0xFF
    
    with pytest.raises(InvalidTag):
        decrypt_evidence(bytes(tampered_ciphertext), nonce)

def test_modify_nonce_fails():
    """4. Modify nonce → decryption fails."""
    plaintext = b"Sensitive Data 2"
    ciphertext, nonce = encrypt_evidence(plaintext)
    
    # Tamper with nonce
    nonce_bytes = bytearray(bytes.fromhex(nonce))
    nonce_bytes[0] ^= 0xFF
    tampered_nonce = nonce_bytes.hex()
    
    # Decryption fails usually with InvalidTag or ValueError
    with pytest.raises(Exception):
        decrypt_evidence(ciphertext, tampered_nonce)

def test_sha256_match():
    """5. Correct decrypted plaintext → SHA-256 matches stored hash."""
    plaintext = b"Data for hashing"
    expected_hash = calculate_sha256(plaintext)
    
    ciphertext, nonce = encrypt_evidence(plaintext)
    decrypted = decrypt_evidence(ciphertext, nonce)
    
    computed_hash = calculate_sha256(decrypted)
    assert computed_hash == expected_hash

def test_existing_seeded_evidence():
    """6. Existing seeded evidence verification behavior."""
    from app.models.models import Evidence
    from app.services.evidence_service import verify_evidence_integrity
    from app.models.models import User
    from app.core.database import SessionLocal
    
    db_session = SessionLocal()
    try:
        # Find active admin user for requestor
        user = db_session.query(User).first()
        
        # Verify the specific seeded evidence
        evidences = db_session.query(Evidence).all()
        assert len(evidences) > 0, "No evidence in DB"
        
        for ev in evidences:
            res = verify_evidence_integrity(db_session, ev, user, "127.0.0.1")
            assert res["match"] is True, f"Failed verification for {ev.original_filename}: {res['status']}"
            assert res["status"] == "HASH MATCH — INTEGRITY VERIFIED"
    finally:
        db_session.close()
