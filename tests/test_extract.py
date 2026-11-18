from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.schemas import Invoice

client = TestClient(app)

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_extract_ok():
    fake = Invoice(vendor="ACME", invoice_number="INV-1", total=100.0)
    with patch("app.routers.extract.extract_invoice", AsyncMock(return_value=fake)):
        r = client.post("/v1/extract", json={"text": "Invoice INV-1 from ACME total 100"})
    assert r.status_code == 200
    assert r.json()["data"]["vendor"] == "ACME"

def test_empty_text_rejected():
    assert client.post("/v1/extract", json={"text": ""}).status_code == 422