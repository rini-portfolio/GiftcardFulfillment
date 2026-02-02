import os
import sys
import pytest

# ensure package dir is importable
here = os.path.dirname(__file__)
pkg_dir = os.path.abspath(os.path.join(here, ".."))
if pkg_dir not in sys.path:
    sys.path.insert(0, pkg_dir)

import fiserv_client


class TestFiservClientIssue:
    """Test FiservClient.issue() method"""

    def test_issue_success(self, requests_mock, fiserv_url):
        """Test successful giftcard issuance"""
        requests_mock.post(
            f"{fiserv_url}/issue",
            json={"giftcardId": "gc-123"},
            status_code=200
        )

        client = fiserv_client.FiservClient(fiserv_url, api_key="test-key", timeout=1, retries=0)
        gid = client.issue("user@example.com", 25.0)
        assert gid == "gc-123"

    def test_issue_with_retries(self, requests_mock, fiserv_url):
        """Test issuance with retry logic"""
        requests_mock.post(
            f"{fiserv_url}/issue",
            [
                {"status_code": 500, "text": "error"},
                {"json": {"giftcardId": "gc-456"}, "status_code": 200},
            ]
        )

        client = fiserv_client.FiservClient(fiserv_url, api_key="test-key", timeout=1, retries=1)
        gid = client.issue("user@example.com", 10.0)
        assert gid == "gc-456"

    def test_issue_invalid_json_response(self, requests_mock, fiserv_url):
        """Test handling of invalid JSON response"""
        requests_mock.post(
            f"{fiserv_url}/issue",
            text="not-json",
            status_code=200
        )

        client = fiserv_client.FiservClient(fiserv_url, api_key="test-key", timeout=1, retries=0)
        with pytest.raises(fiserv_client.FiservError):
            client.issue("user@example.com", 10.0)

    def test_issue_missing_giftcard_id(self, requests_mock, fiserv_url):
        """Test handling of missing giftcardId in response"""
        requests_mock.post(
            f"{fiserv_url}/issue",
            json={"status": "ok"},  # missing giftcardId
            status_code=200
        )

        client = fiserv_client.FiservClient(fiserv_url, api_key="test-key", timeout=1, retries=0)
        with pytest.raises(fiserv_client.FiservError):
            client.issue("user@example.com", 10.0)

    def test_issue_timeout_then_success(self, requests_mock, fiserv_url):
        """Test timeout handling with retry"""
        requests_mock.post(
            f"{fiserv_url}/issue",
            [
                {"exc": Exception("timeout")},
                {"json": {"giftcardId": "gc-789"}, "status_code": 200},
            ]
        )

        client = fiserv_client.FiservClient(fiserv_url, api_key="test-key", timeout=1, retries=1)
        gid = client.issue("user@example.com", 50.0)
        assert gid == "gc-789"

    def test_issue_all_retries_fail(self, requests_mock, fiserv_url):
        """Test failure after all retries exhausted"""
        requests_mock.post(
            f"{fiserv_url}/issue",
            status_code=503
        )

        client = fiserv_client.FiservClient(fiserv_url, api_key="test-key", timeout=1, retries=2)
        with pytest.raises(fiserv_client.FiservError):
            client.issue("user@example.com", 10.0)


class TestFiservClientValidation:
    """Test FiservClient parameter validation"""

    def test_issue_with_empty_email(self, requests_mock, fiserv_url):
        """Test issuance with empty email"""
        requests_mock.post(
            f"{fiserv_url}/issue",
            json={"giftcardId": "gc-123"},
            status_code=200
        )

        client = fiserv_client.FiservClient(fiserv_url, api_key="test-key", timeout=1, retries=0)
        # Should still send request (validation is at app level)
        gid = client.issue("", 25.0)
        assert gid == "gc-123"

    def test_issue_with_negative_amount(self, requests_mock, fiserv_url):
        """Test issuance with negative amount"""
        requests_mock.post(
            f"{fiserv_url}/issue",
            json={"giftcardId": "gc-123"},
            status_code=200
        )

        client = fiserv_client.FiservClient(fiserv_url, api_key="test-key", timeout=1, retries=0)
        # Client should still send (validation at app level)
        gid = client.issue("user@example.com", -10.0)
        assert gid == "gc-123"
