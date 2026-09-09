# tests/test_api_integration.py
"""Integration tests for the FastAPI server."""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.api import app
from app.core.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_agents():
    """Test listing all agents."""
    response = client.get("/agents/")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 15
    assert "product_director" in data["agents"]


def test_execute_product_director():
    """Test executing the product director agent."""
    response = client.post(
        "/agents/product_director/execute",
        json={"project_id": "test-123", "action": "execute"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "test-123" in data["message"]


def test_execute_invalid_agent():
    """Test executing an invalid agent returns 404."""
    response = client.post(
        "/agents/invalid_agent/execute",
        json={"project_id": "test-123", "action": "execute"}
    )
    assert response.status_code == 404


def test_create_project():
    """Test creating a new project."""
    response = client.post(
        "/agents/projects",
        params={
            "project_id": "proj-001",
            "title": "Test Ebook",
            "niche": "Test Niche",
            "product_brief": "Test brief"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["id"] == "proj-001"


def test_get_project():
    """Test retrieving a project."""
    # First create a project
    client.post(
        "/agents/projects",
        params={
            "project_id": "proj-002",
            "title": "Test Ebook 2",
            "niche": "Test Niche 2"
        }
    )
    
    # Then retrieve it
    response = client.get("/agents/projects/proj-002")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["title"] == "Test Ebook 2"
    assert data["data"]["niche"] == "Test Niche 2"


def test_get_nonexistent_project():
    """Test retrieving a non-existent project returns 404."""
    response = client.get("/agents/projects/nonexistent")
    assert response.status_code == 404


def test_update_project_status():
    """Test updating project status."""
    # Create a project first
    client.post(
        "/agents/projects",
        params={
            "project_id": "proj-003",
            "title": "Test Ebook 3",
            "niche": "Test Niche 3"
        }
    )
    
    # Update status
    response = client.patch("/agents/projects/proj-003/status", params={"status": "researching"})
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status"] == "researching"


def test_update_project_status_invalid():
    """Test updating project status with invalid value."""
    response = client.patch("/agents/projects/proj-003/status", params={"status": "invalid_status"})
    assert response.status_code == 400
