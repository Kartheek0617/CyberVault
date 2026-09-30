import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.models import Evidence
from app.security.encryption import encrypt_evidence, calculate_sha256
from app.core.config import get_settings

evidence_data = {
    "network_capture_2026-09-14.pcap": b"FICTIONAL PCAP CONTENT: TCP SYN flood detected from 198.51.100.42. Port 22 brute force. 4729 failed auth attempts in 180 seconds. [DEMO DATA - NOT REAL]",
    "server_access_log_excerpt.txt": b"FICTIONAL LOG: 2026-09-14 02:31:17 FAILED_LOGIN root FROM 198.51.100.42\n2026-09-14 02:31:18 FAILED_LOGIN admin FROM 198.51.100.42\n[DEMO DATA - NOT REAL]",
    "ransomware_sample_metadata.txt": b"FICTIONAL MALWARE METADATA: SHA256: DEMO_HASH_ONLY. File: invoice.pdf.exe. Mutex: Global\\XWorm_v2.1. C2: 203.0.113.99:4444. [DEMO DATA - NOT REAL]",
    "usb_activity_report.csv": b"FICTIONAL CSV:\nTimestamp,Device,Action,FileCount\n2026-09-10 17:45:00,USB_WD_1TB,CONNECTED,0\n2026-09-10 17:47:32,USB_WD_1TB,COPY,1247\n[DEMO DATA - NOT REAL]",
}

def migrate():
    settings = get_settings()
    db = SessionLocal()
    storage_path = settings.evidence_storage_path

    print("Migrating seeded evidence files using the local persistent ENCRYPTION_KEY...")
    
    evidences = db.query(Evidence).all()
    for ev in evidences:
        content = evidence_data.get(ev.original_filename)
        if not content:
            print(f"Skipping {ev.original_filename} - No known plaintext")
            continue
            
        print(f"Re-encrypting {ev.original_filename}...")
        
        # Verify hash hasn't somehow changed
        sha256 = calculate_sha256(content)
        assert sha256 == ev.sha256_hash, "Hash mismatch, cannot migrate safely"
        
        # Encrypt with current persistent key!
        ciphertext, nonce_hex = encrypt_evidence(content)
        
        # Rewrite the physical file
        file_path = storage_path / ev.storage_filename
        with open(file_path, "wb") as f:
            f.write(ciphertext)
            
        # Update nonce in DB
        ev.encryption_nonce = nonce_hex
        db.add(ev)
        
    db.commit()
    print("Migration complete. All 4 seeded evidence files are now decryptable with the local .env key.")
    
if __name__ == "__main__":
    migrate()
