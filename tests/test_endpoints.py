import base64
from io import BytesIO
from PIL import Image
import pytest
from fastapi.testclient import TestClient
from web_server import app, MAX_UPLOAD_BYTES
from cloud_ui import handle_request, pipeline

@pytest.fixture
def client():
    return TestClient(app)

def make_png_bytes():
    buf = BytesIO()
    im = Image.new("RGB", (64, 64), color="blue")
    im.save(buf, format="PNG")
    return buf.getvalue()

def test_fastapi_home_redirect(client):
    res = client.get("/", follow_redirects=False)
    assert res.status_code == 307
    assert res.headers["location"] == "/static/index.html"

def test_fastapi_status(client):
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert "ai_available" in data
    assert "dataset_available" in data
    assert data["dataset_available"] is True

def test_fastapi_analyze_scam(client):
    res = client.post(
        "/api/analyze",
        json={"text": "Your electricity will be cut tonight at 9:30 PM. Pay bill: http://bit.ly/pay", "language": "en"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["verdict"] == "SCAM"
    assert "red_flags" in data
    assert "recommended_actions" in data
    assert "references" in data

def test_fastapi_analyze_empty(client):
    res = client.post("/api/analyze", json={"text": "   ", "language": "en"})
    assert res.status_code == 422

def test_fastapi_extract_no_api_key(client):
    png = make_png_bytes()
    res = client.post("/api/extract", content=png, headers={"Content-Type": "image/png"})
    assert res.status_code == 422
    assert res.json()["detail"] == "unavailable"

def test_fastapi_extract_oversized(client):
    oversized = b"0" * (MAX_UPLOAD_BYTES + 50)
    res = client.post("/api/extract", content=oversized, headers={"Content-Type": "image/png"})
    assert res.status_code == 413
    assert res.json()["detail"] == "too_large"

def test_cloud_ui_handle_request_status():
    p = pipeline()
    req = {"id": "req-status", "path": "/api/status", "payload": None}
    res = handle_request(req, p, None)
    assert res["status"] == 200
    assert res["body"]["dataset_available"] is True
    assert res["body"]["ai_available"] is False

def test_cloud_ui_handle_request_analyze():
    p = pipeline()
    req = {
        "id": "req-analyze",
        "path": "/api/analyze",
        "payload": {"text": "A/C XX1234 debited by Rs 500 at Store via UPI. Avail Bal: Rs 5000.", "language": "en"},
    }
    res = handle_request(req, p, None)
    assert res["status"] == 200
    assert res["body"]["verdict"] == "SAFE"

def test_cloud_ui_handle_request_invalid_path():
    p = pipeline()
    req = {"id": "req-bad", "path": "/api/unknown", "payload": {}}
    res = handle_request(req, p, None)
    assert res["status"] == 422
