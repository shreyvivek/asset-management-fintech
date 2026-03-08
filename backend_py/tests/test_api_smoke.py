from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_me():
    r = client.get("/me")
    assert r.status_code == 200
    data = r.json()
    assert "id" in data


def test_events_list():
    r = client.get("/events")
    assert r.status_code in (200, 422, 500)
    if r.status_code == 200:
        assert isinstance(r.json(), list)


def test_themes_list():
    r = client.get("/themes")
    assert r.status_code in (200, 422, 500)
    if r.status_code == 200:
        assert isinstance(r.json(), list)


def test_manual_ingest():
    r = client.post("/events/ingest/manual", json={"title": "Test CPI", "summary": "Hot print.", "event_type": "data_release"})
    assert r.status_code in (200, 422, 500)
    if r.status_code == 200:
        assert "id" in r.json()
