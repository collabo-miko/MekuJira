"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns healthy."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root(self, client):
        """Test root returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["version"] == "0.1.0"


class TestExcelAPI:
    """Tests for Excel upload API."""

    def test_list_sessions_empty(self, client):
        """Test listing sessions when empty."""
        with patch("app.api.routes.excel.SessionRepository.get_all", new_callable=AsyncMock) as mock:
            mock.return_value = []
            response = client.get("/api/excel/sessions")
            assert response.status_code == 200
            assert response.json() == []


class TestDocumentsAPI:
    """Tests for Documents API."""

    def test_list_documents_empty(self, client):
        """Test listing documents when empty."""
        with patch("app.api.routes.documents.DocumentRepository.get_all", new_callable=AsyncMock) as mock:
            mock.return_value = []
            response = client.get("/api/documents")
            assert response.status_code == 200
            assert response.json() == []
