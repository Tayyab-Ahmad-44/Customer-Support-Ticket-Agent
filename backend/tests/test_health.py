from fastapi.testclient import TestClient

from application import application


def test_health_returns_ok_status():
    response = TestClient(application).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
