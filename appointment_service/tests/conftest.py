"""
Test fixtures and configuration for user_service tests
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    from main import app
    with TestClient(app) as test_client:
        yield test_client
