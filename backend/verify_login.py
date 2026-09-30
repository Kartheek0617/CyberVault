import os
import sys

# Ensure backend directory is in the path
sys.path.insert(0, os.path.abspath('.'))

from fastapi.testclient import TestClient
from app.main import app
from app.api.auth import _login_attempts

def check_login():
    client = TestClient(app)
    
    # 0. Set IP address manually
    headers = {"X-Forwarded-For": "192.168.1.100"}  
    # Wait, Starlette TestClient uses testclient ip "testclient" by default. 
    # Let's just use it without headers and clear it before test.
    _login_attempts.clear()

    # 1. Correct credentials can log in
    print("Testing Correct login...")
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@CyberVault2026!"})
    assert resp.status_code == 200, f"Failed correct login: {resp.text}"
    print("Correct login: PASS")

    # 2. Incorrect credentials rejected
    print("Testing Incorrect login...")
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "WrongPassword!"})
    assert resp.status_code == 401, f"Expected 401: {resp.text}"
    print("Incorrect login: PASS")

    # 3. Repeated failed attempts trigger rate limiting (limit is 5)
    print("Spamming to hit rate limit...")
    for _ in range(4):
        client.post("/api/auth/login", json={"username": "admin", "password": "WrongPassword!"})
    
    # Next one should be 429
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "WrongPassword!"})
    assert resp.status_code == 429, f"Expected 429: {resp.text}"
    print("Rate limiting 429 triggers: PASS")

    # 4. Correct credentials still get 429 during lockout
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@CyberVault2026!"})
    assert resp.status_code == 429, "Expected to be blocked due to IP limit"
    
    # 5. Use Reset endpoint
    print("Using Reset endpoint...")
    resp = client.post("/api/auth/reset-rate-limit")
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    print("Reset endpoint: PASS")

    # 6. Correct credentials login successfully after reset
    print("Testing Correct login after reset...")
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@CyberVault2026!"})
    assert resp.status_code == 200, "Failed correct login after reset"
    print("Correct login after reset: PASS")
    
    print("ALL VERIFICATIONS COMPLETE")

if __name__ == "__main__":
    check_login()
