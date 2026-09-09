# tests/test_mcp.py
"""Tests for MCP servers."""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def test_google_drive_mcp_module_exists():
    """Test that Google Drive MCP server module can be imported."""
    from app.mcp.google_drive_mcp_server import app
    assert app is not None
    assert app.title == "Google Drive MCP Server"


def test_google_drive_mcp_health_endpoint():
    """Test health check endpoint."""
    from app.mcp.google_drive_mcp_server import app
    
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_google_drive_mcp_list_tools():
    """Test list tools endpoint."""
    from app.mcp.google_drive_mcp_server import app
    
    client = TestClient(app)
    response = client.post("/mcp/tools/list")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    tool_names = [t["name"] for t in data["tools"]]
    assert "upload_file" in tool_names
    assert "create_folder" in tool_names


def test_google_drive_mcp_create_folder():
    """Test create folder endpoint with mocked service."""
    from app.mcp.google_drive_mcp_server import app
    
    client = TestClient(app)
    
    with patch('app.mcp.google_drive_mcp_server._get_drive_service') as mock_get_service:
        mock_service = MagicMock()
        mock_service.files().create().execute().return_value = {
            'id': 'test_folder_id',
            'name': 'Test Folder',
            'webViewLink': 'https://drive.google.com/drive/folders/test'
        }
        mock_get_service.return_value = mock_service
        
        response = client.post("/folders/create", json={"name": "Test Folder"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


def test_google_drive_mcp_upload_file():
    """Test upload file endpoint with mocked service."""
    from app.mcp.google_drive_mcp_server import app
    
    client = TestClient(app)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test content")
        temp_path = f.name
    
    try:
        with patch('app.mcp.google_drive_mcp_server._get_drive_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.files().create().execute().return_value = {
                'id': 'test_file_id',
                'name': 'test.txt',
                'mimeType': 'text/plain',
                'size': 12,
                'webViewLink': 'https://drive.google.com/file/d/test'
            }
            mock_get_service.return_value = mock_service
            
            response = client.post("/files/upload", json={"file_path": temp_path})
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_google_drive_mcp_project_sync():
    """Test project sync endpoint."""
    from app.mcp.google_drive_mcp_server import app
    
    client = TestClient(app)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("project content")
        temp_path = f.name
    
    try:
        with patch('app.mcp.google_drive_mcp_server._get_drive_service') as mock_get_service:
            mock_service = MagicMock()
            
            # Mock folder creation
            call_count = [0]
            def mock_side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return MagicMock(execute=MagicMock(return_value={'id': 'test_folder_id', 'name': 'Test Project'}))
                else:
                    return MagicMock(execute=MagicMock(return_value={'id': 'file_id', 'name': 'test.md'}))
            
            mock_service.files().create.side_effect = lambda *args, **kwargs: mock_side_effect()
            mock_get_service.return_value = mock_service
            
            response = client.post("/project-sync", json={
                "name": "Test Project",
                "file_paths": [temp_path]
            })
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["folder_id"] == "test_folder_id"
            assert data["uploaded_count"] == 1
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_google_drive_mcp_file_not_found():
    """Test upload with non-existent file."""
    from app.mcp.google_drive_mcp_server import app
    
    client = TestClient(app)
    response = client.post("/files/upload", json={"file_path": "/nonexistent/file.txt"})
    assert response.status_code == 404


def test_google_drive_mcp_list_files():
    """Test list files endpoint."""
    from app.mcp.google_drive_mcp_server import app
    
    client = TestClient(app)
    
    with patch('app.mcp.google_drive_mcp_server._get_drive_service') as mock_get_service:
        from unittest.mock import MagicMock
        mock_service = MagicMock()
        
        # Create the mock chain: service.files().list().execute()
        list_mock = MagicMock()
        list_mock.execute.return_value = {
            'files': [
                {'id': '1', 'name': 'test.txt', 'mimeType': 'text/plain'},
                {'id': '2', 'name': 'test.pdf', 'mimeType': 'application/pdf'}
            ]
        }
        
        files_mock = MagicMock()
        files_mock.list.return_value = list_mock
        
        mock_service.files.return_value = files_mock
        mock_get_service.return_value = mock_service
        
        response = client.get("/files/list")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["files"]) == 2