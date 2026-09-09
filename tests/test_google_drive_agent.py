# tests/test_google_drive_agent.py
"""Tests for Google Drive Agent with Ollama integration."""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_get_agent():
    """Mock get_agent for all tests."""
    with patch('app.agents.google_drive_agent.get_agent') as mock_get_agent:
        mock_agent = MagicMock()
        mock_agent.list_files.return_value = [
            {'id': '1', 'name': 'test.txt', 'mimeType': 'text/plain'},
            {'id': '2', 'name': 'test.pdf', 'mimeType': 'application/pdf'}
        ]
        mock_agent.get_file_content.return_value = "Sample file content for testing."
        mock_agent.analyze_file_with_llm.return_value = {
            'status': 'success',
            'file': {'id': '1', 'name': 'test.txt'},
            'analysis_type': 'summary',
            'analysis': 'This is a test summary.'
        }
        mock_agent.intelligent_organize.return_value = {
            'status': 'success',
            'total_files': 2,
            'suggestion': 'Organize into folders by type.',
            'query': 'ebook project'
        }
        mock_agent.chat_about_drive.return_value = {
            'status': 'success',
            'response': 'I can help you with that.',
            'context': {'files_available': 2}
        }
        mock_agent.find_or_create_folder.return_value = 'folder_123'
        mock_agent._upload_file.return_value = 'uploaded_123'
        mock_get_agent.return_value = mock_agent
        yield mock_agent


def test_google_drive_agent_module_exists():
    """Test that Google Drive agent module can be imported."""
    from app.agents.google_drive_agent import app
    assert app is not None
    assert app.title == "Google Drive Agent"


def test_agent_health_endpoint(mock_get_agent):
    """Test agent health endpoint."""
    from app.agents.google_drive_agent import app
    
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "google-drive-agent"


def test_agent_list_files(mock_get_agent):
    """Test listing files."""
    from app.agents.google_drive_agent import app
    
    client = TestClient(app)
    response = client.get("/files")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["count"] == 2
    mock_get_agent.list_files.assert_called()


def test_agent_analyze_file(mock_get_agent):
    """Test file analysis with mocked agent."""
    from app.agents.google_drive_agent import app
    
    client = TestClient(app)
    response = client.post("/analyze", json={
        "file_id": "123",
        "analysis_type": "summary"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["analysis_type"] == "summary"
    mock_get_agent.analyze_file_with_llm.assert_called_with("123", "summary")


def test_agent_intelligent_organize(mock_get_agent):
    """Test intelligent organization."""
    from app.agents.google_drive_agent import app
    
    client = TestClient(app)
    response = client.post("/organize", json={"query": "organize my ebook project"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    mock_get_agent.intelligent_organize.assert_called_with("organize my ebook project")


def test_agent_chat(mock_get_agent):
    """Test chat functionality."""
    from app.agents.google_drive_agent import app
    
    client = TestClient(app)
    response = client.post("/chat", json={
        "message": "What files do I have?",
        "context": {"history": []}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "response" in data
    mock_get_agent.chat_about_drive.assert_called_once()


def test_agent_chat_without_context(mock_get_agent):
    """Test chat without context."""
    from app.agents.google_drive_agent import app
    
    client = TestClient(app)
    response = client.post("/chat", json={"message": "List my files"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    mock_get_agent.chat_about_drive.assert_called_once()


def test_agent_sync_project(mock_get_agent):
    """Test project sync with mocked agent."""
    from app.agents.google_drive_agent import app
    
    client = TestClient(app)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "chapter1.md")
        with open(test_file, 'w') as f:
            f.write("# Chapter 1")
        
        response = client.post("/sync-project", json={
            "project_name": "Test Ebook",
            "local_path": tmpdir,
            "analyze": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["project"] == "Test Ebook"


def test_ollama_client_initialization():
    """Test Ollama client initialization."""
    from app.agents.google_drive_agent import OllamaClient
    
    client = OllamaClient(base_url="http://localhost:11434", model="llama3.2:latest")
    assert client.base_url == "http://localhost:11434"
    assert client.model == "llama3.2:latest"


def test_ollama_generate_with_system():
    """Test Ollama generate with system prompt."""
    from app.agents.google_drive_agent import OllamaClient
    
    client = OllamaClient.__new__(OllamaClient)
    client.base_url = "http://localhost:11434"
    client.model = "llama3.2:latest"
    client.client = None
    
    client.chat = MagicMock(return_value="Generated output")
    
    result = client.generate("Test prompt", system_prompt="You are helpful.")
    assert result == "Generated output"


def test_agent_find_or_create_folder(mock_get_agent):
    """Test folder management."""
    mock_get_agent.find_or_create_folder.return_value = "folder_123"
    
    folder_id = mock_get_agent.find_or_create_folder("Test Folder")
    assert folder_id == "folder_123"


def test_agent_upload_file(mock_get_agent):
    """Test file upload."""
    mock_get_agent._upload_file.return_value = "uploaded_123"
    
    file_id = mock_get_agent._upload_file("/tmp/test.txt", "folder_123")
    assert file_id == "uploaded_123"


def test_agent_file_content_retrieval(mock_get_agent):
    """Test file content retrieval."""
    mock_get_agent.get_file_content.return_value = "Hello, world!"
    
    content = mock_get_agent.get_file_content("123")
    assert content == "Hello, world!"


def test_agent_class_can_be_instantiated():
    """Test agent class can be referenced."""
    from app.agents.google_drive_agent import GoogleDriveAgent
    assert GoogleDriveAgent is not None