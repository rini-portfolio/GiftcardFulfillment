import pytest
import os
import sys

# ensure package dir is importable
here = os.path.dirname(__file__)
pkg_dir = os.path.abspath(os.path.join(here, ".."))
if pkg_dir not in sys.path:
    sys.path.insert(0, pkg_dir)


@pytest.fixture
def fiserv_url():
    """Mock Fiserv API URL"""
    return "http://localhost:8090"


@pytest.fixture
def valid_issue_request():
    """Valid giftcard issue request"""
    return {
        "email": "customer@example.com",
        "amount": 100.0
    }


@pytest.fixture
def invalid_issue_request():
    """Invalid giftcard issue request (missing fields)"""
    return {
        "email": "customer@example.com"
        # missing amount
    }
