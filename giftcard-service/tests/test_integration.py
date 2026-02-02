import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# ensure package dir is importable
here = os.path.dirname(__file__)
pkg_dir = os.path.abspath(os.path.join(here, ".."))
if pkg_dir not in sys.path:
    sys.path.insert(0, pkg_dir)

import importlib.util
spec = importlib.util.spec_from_file_location("app", os.path.join(pkg_dir, "app.py"))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)

from fastapi.testclient import TestClient

client = TestClient(app_module.app)


class MockFiservClient:
    """Mock Fiserv client for integration testing"""
    def __init__(self, gid="gc-integration", should_fail=False):
        self.gid = gid
        self.should_fail = should_fail
        self.call_count = 0

    def issue(self, email, amount):
        self.call_count += 1
        if self.should_fail:
            raise Exception("Fiserv service error")
        return self.gid


class TestGiftcardServiceIntegration:
    """Integration tests for giftcard service"""

    def test_end_to_end_issue_flow(self, monkeypatch):
        """Test complete flow from request to response"""
        mock_client = MockFiservClient(gid="gc-e2e-123")
        monkeypatch.setattr(app_module, "fiserv_client", mock_client)

        resp = client.post("/issue", json={
            "email": "integration@test.com",
            "amount": 250.0
        })

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "Gift card issued"
        assert body["giftcard"]["giftcardId"] == "gc-e2e-123"
        assert body["giftcard"]["email"] == "integration@test.com"
        assert body["giftcard"]["amount"] == 250.0
        assert mock_client.call_count == 1

    def test_concurrent_requests(self, monkeypatch):
        """Test handling multiple concurrent-like requests"""
        mock_client = MockFiservClient()
        monkeypatch.setattr(app_module, "fiserv_client", mock_client)

        # Simulate multiple requests
        for i in range(3):
            resp = client.post("/issue", json={
                "email": f"user{i}@example.com",
                "amount": float(50 + i * 10)
            })
            assert resp.status_code == 200

        assert mock_client.call_count == 3

    def test_error_recovery(self, monkeypatch):
        """Test that service recovers from Fiserv errors"""
        # First request fails
        mock_client1 = MockFiservClient(should_fail=True)
        monkeypatch.setattr(app_module, "fiserv_client", mock_client1)

        resp1 = client.post("/issue", json={
            "email": "user@example.com",
            "amount": 100.0
        })
        assert resp1.status_code == 502

        # Second request succeeds with new client
        mock_client2 = MockFiservClient(gid="gc-recovery-123")
        monkeypatch.setattr(app_module, "fiserv_client", mock_client2)

        resp2 = client.post("/issue", json={
            "email": "user@example.com",
            "amount": 100.0
        })
        assert resp2.status_code == 200
        assert resp2.json()["giftcard"]["giftcardId"] == "gc-recovery-123"

    def test_response_structure(self, monkeypatch):
        """Test that response has correct structure"""
        mock_client = MockFiservClient(gid="gc-struct-123")
        monkeypatch.setattr(app_module, "fiserv_client", mock_client)

        resp = client.post("/issue", json={
            "email": "struct@test.com",
            "amount": 75.0
        })

        assert resp.status_code == 200
        body = resp.json()

        # Check required fields
        assert "status" in body
        assert "giftcard" in body
        assert "giftcardId" in body["giftcard"]
        assert "email" in body["giftcard"]
        assert "amount" in body["giftcard"]
