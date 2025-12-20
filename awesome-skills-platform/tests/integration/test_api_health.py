"""
Integration tests for health check endpoints.
"""
import pytest


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root_endpoint(self, test_client):
        """Test root endpoint returns welcome message."""
        response = test_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Agent Platform" in data["message"] or "Welcome" in data["message"]

    def test_health_endpoint(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
