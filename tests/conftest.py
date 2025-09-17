"""
Configuration file for pytest tests
"""

import pytest
from eitaayar import Client


@pytest.fixture
def client():
    """Fixture for creating a test client"""
    return Client("test_token", enable_logging=False)


@pytest.fixture
def mock_response():
    """Fixture for creating mock responses"""
    def _create_response(ok=True, result=None, error=None, error_code=None):
        data = {"ok": ok}
        if result:
            data["result"] = result
        if error:
            data["error"] = error
        if error_code:
            data["error_code"] = error_code
        return data
    return _create_response