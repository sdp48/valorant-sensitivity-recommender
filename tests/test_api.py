from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "players" in data


def test_recommend():
    payload = {
        "dpi": 800,
        "aim_style": "hybrid",
        "goal": "balanced",
        "pad": "medium",
        "current_sensitivity": None,
    }
    r = client.post("/recommend", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "suggested_sens" in data
    assert "mid_edpi" in data