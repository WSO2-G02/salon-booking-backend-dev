"""
API endpoint tests for user_service
"""
import pytest


class TestHealthEndpoint:
    """Tests for health check endpoint"""

    def test_health_check_returns_200(self, client):
        """Health endpoint should return 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_response_format(self, client):
        """Health endpoint should return proper JSON structure"""
        response = client.get("/health")
        data = response.json()
        assert "status" in data


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_returns_200(self, client):
        """Root endpoint should return 200 OK"""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_service_info(self, client):
        """Root endpoint should return service information"""
        response = client.get("/")
        data = response.json()
        assert "service" in data
        assert "status" in data
        assert data["status"] == "running"


class TestDocsEndpoint:
    """Tests for documentation endpoints"""

    def test_docs_available(self, client):
        """OpenAPI docs should be available"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema_available(self, client):
        """OpenAPI schema should be available"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
