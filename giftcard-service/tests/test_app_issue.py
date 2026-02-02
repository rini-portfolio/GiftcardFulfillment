import os
import sys
import types
import pytest

# ensure package dir is importable
here = os.path.dirname(__file__)
pkg_dir = os.path.abspath(os.path.join(here, ".."))
if pkg_dir not in sys.path:
    sys.path.insert(0, pkg_dir)

# import app by file import so we get the FastAPI app object
import importlib.util
spec = importlib.util.spec_from_file_location("app", os.path.join(pkg_dir, "app.py"))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)

from fastapi.testclient import TestClient

client = TestClient(app_module.app)


class DummyClient:
    def __init__(self, gid=None, raise_exc=False):
        self.gid = gid
        self.raise_exc = raise_exc

    def issue(self, email, amount):
        if self.raise_exc:
            raise Exception("fiserv down")
        return self.gid or "gc-test"


class TestIssueEndpoint:
    """Test /issue endpoint"""

    def test_issue_success(self, monkeypatch, valid_issue_request):
        """Test successful giftcard issuance"""
        monkeypatch.setattr(app_module, "fiserv_client", DummyClient(gid="gc-xyz"))

        resp = client.post("/issue", json=valid_issue_request)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "Gift card issued"
        assert body["giftcard"]["giftcardId"] == "gc-xyz"
        assert body["giftcard"]["email"] == valid_issue_request["email"]
        assert body["giftcard"]["amount"] == valid_issue_request["amount"]

    def test_issue_fiserv_error(self, monkeypatch, valid_issue_request):
        """Test handling of Fiserv errors"""
        monkeypatch.setattr(app_module, "fiserv_client", DummyClient(raise_exc=True))

        resp = client.post("/issue", json=valid_issue_request)
        assert resp.status_code == 502
        assert "Error contacting Fiserv" in resp.json()["detail"]

    def test_issue_missing_email(self, monkeypatch):
        """Test request with missing email"""
        monkeypatch.setattr(app_module, "fiserv_client", DummyClient(gid="gc-123"))

        resp = client.post("/issue", json={"amount": 100.0})
        assert resp.status_code == 400
        assert "Missing email or amount" in resp.json()["detail"]

    def test_issue_missing_amount(self, monkeypatch):
        """Test request with missing amount"""
        monkeypatch.setattr(app_module, "fiserv_client", DummyClient(gid="gc-123"))

        resp = client.post("/issue", json={"email": "user@example.com"})
        assert resp.status_code == 400
        assert "Missing email or amount" in resp.json()["detail"]

    def test_issue_no_fiserv_configured(self, monkeypatch, valid_issue_request):
        """Test when Fiserv is not configured"""
        monkeypatch.setattr(app_module, "fiserv_client", None)

        resp = client.post("/issue", json=valid_issue_request)
        assert resp.status_code == 500
        assert "not configured" in resp.json()["detail"]

    def test_issue_various_amounts(self, monkeypatch):
        """Test issuance with various amounts"""
        monkeypatch.setattr(app_module, "fiserv_client", DummyClient(gid="gc-var"))

        for amount in [0.01, 10.0, 100.0, 1000.0]:
            resp = client.post("/issue", json={"email": "test@example.com", "amount": amount})
            assert resp.status_code == 200
            body = resp.json()
            assert body["giftcard"]["amount"] == amount
