from fastapi.testclient import TestClient
from app import app, verify_token, SECRET_KEY, ALGORITHM
from jose import jwt

client = TestClient(app)


def test_valid_token():
    token = jwt.encode(
        {"username": "testuser", "role": "doctor"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    result = verify_token(token)

    assert result["username"] == "testuser"


def test_invalid_token():
    result = verify_token("invalid-token")
    assert result is None


def test_dashboard_loads():
    response = client.get("/dashboard")
    assert response.status_code == 200


def test_unauthorized_audit_logs():
    response = client.get("/api/audit-logs")
    assert response.status_code == 200
    assert response.json()["error"] == "Unauthorized"
import time


def test_dashboard_performance():
    start_time = time.time()

    response = client.get("/dashboard")

    end_time = time.time()

    response_time = end_time - start_time

    assert response.status_code == 200
    assert response_time < 2

    print(f"\nDashboard response time: {response_time:.3f} seconds")
import time


def test_dashboard_performance():
    start_time = time.time()

    response = client.get("/dashboard")

    end_time = time.time()

    response_time = end_time - start_time

    assert response.status_code == 200
    assert response_time < 2

    print(f"\nDashboard response time: {response_time:.3f} seconds")