import sys
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.models import User
from app.security.jwt import create_access_token
from app.security.dependencies import get_db
import uuid

# Dependency override not needed, we can test with actual DB
db = SessionLocal()

def test_regression_jwt_uuid():
    # 1. Take a known user from the setup DB
    user = db.query(User).first()
    assert user is not None, "User should exist in the pre-populated DB"

    # 2. Get their UUID, but intentionally create a token with a string subject to mirror the bug
    user_id_str = str(user.id)
    token = create_access_token(subject=user_id_str, role=user.role.value)

    # 3. Simulate getting cases which invokes get_current_user dependencies
    client = TestClient(app)
    response = client.get(
        "/api/cases",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Bug not fully fixed? Details: {response.text}"
    data = response.json()
    assert "cases" in data
    assert len(data["cases"]) > 0, "Expected existing cases to be returned."
    print("Regression Test Passed. Cases retrieved:", len(data["cases"]))

if __name__ == "__main__":
    test_regression_jwt_uuid()
