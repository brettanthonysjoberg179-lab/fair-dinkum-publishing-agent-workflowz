# tests/test_bot.py
"""Tests for Google Drive Bot."""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_get_bot():
    """Patch get_bot for all tests to avoid real Drive auth."""
    mock_bot = MagicMock(name='drivebot')
    mock_commands = MagicMock(name='botcommands')
    
    # Default return values
    mock_commands.cmd_health.return_value = {
        'status': 'healthy',
        'service': 'google-drive-bot',
        'last_check': None
    }
    mock_commands.cmd_help.return_value = {
        'status': 'success',
        'commands': [
            {'name': 'list', 'description': 'List files', 'args': ['query?']},
            {'name': 'info', 'description': 'Get file info', 'args': ['file_id']},
            {'name': 'create-folder', 'description': 'Create folder', 'args': ['name', 'parent_id?']},
            {'name': 'sync', 'description': 'Sync project', 'args': ['project', 'path?']},
            {'name': 'search', 'description': 'Search files', 'args': ['query']},
            {'name': 'health', 'description': 'Health check', 'args': []},
            {'name': 'help', 'description': 'Show this help', 'args': []},
        ]
    }
    mock_commands.cmd_list.return_value = {
        'status': 'success',
        'count': 2,
        'files': [
            {'id': '1', 'name': 'test.txt', 'mimeType': 'text/plain'},
            {'id': '2', 'name': 'test.pdf', 'mimeType': 'application/pdf'}
        ]
    }
    mock_commands.cmd_search.return_value = {
        'status': 'success',
        'count': 1,
        'files': [{'id': '3', 'name': 'ebook.pdf', 'mimeType': 'application/pdf'}]
    }
    mock_commands.cmd_create_folder.return_value = {
        'status': 'success',
        'folder_id': 'folder_123',
        'name': 'Test Folder'
    }
    mock_commands.cmd_sync.return_value = {
        'status': 'success',
        'project': 'Test Project',
        'project_folder_id': 'proj_123',
        'uploaded_count': 1,
        'files': [{'local': 'file.txt', 'drive_id': 'file_123'}]
    }
    mock_commands.handle.return_value = {
        'status': 'error',
        'message': "Unknown command: invalid. Type 'help' for available commands."
    }
    
    with patch('app.bot.google_drive_bot.get_bot', return_value=(mock_bot, mock_commands)):
        yield mock_commands


def test_google_drive_bot_module_exists():
    """Test that Google Drive bot module can be imported."""
    from app.bot.google_drive_bot import app
    assert app is not None
    assert app.title == "Google Drive Bot"


def test_bot_health_endpoint(mock_get_bot):
    """Test bot health endpoint."""
    from app.bot.google_drive_bot import app
    
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "google-drive-bot"
    mock_get_bot.cmd_health.assert_called_once()


def test_bot_help_command(mock_get_bot):
    """Test bot help command."""
    from app.bot.google_drive_bot import app
    
    client = TestClient(app)
    response = client.get("/bot/commands")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "commands" in data
    assert len(data["commands"]) > 0
    mock_get_bot.cmd_help.assert_called_once()


def test_bot_list_command(mock_get_bot):
    """Test bot list command."""
    from app.bot.google_drive_bot import app
    
    client = TestClient(app)
    response = client.post("/bot/command", json={"command": "list"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["count"] == 2
    mock_get_bot.handle.assert_called_once_with("list", None)


def test_bot_search_command(mock_get_bot):
    """Test bot search command."""
    from app.bot.google_drive_bot import app
    
    client = TestClient(app)
    response = client.post("/bot/command", json={
        "command": "search",
        "args": {"query": "ebook"}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    mock_get_bot.handle.assert_called_once_with("search", {"query": "ebook"})


def test_bot_create_folder_command(mock_get_bot):
    """Test bot create folder command."""
    from app.bot.google_drive_bot import app
    
    client = TestClient(app)
    response = client.post("/bot/command", json={
        "command": "create-folder",
        "args": {"name": "Test Folder", "parent_id": "parent123"}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["folder_id"] == "folder_123"
    mock_get_bot.handle.assert_called_once_with("create-folder", {"name": "Test Folder", "parent_id": "parent123"})


def test_bot_unknown_command(mock_get_bot):
    """Test bot unknown command."""
    from app.bot.google_drive_bot import app
    
    client = TestClient(app)
    response = client.post("/bot/command", json={"command": "invalid"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "Unknown command" in data["message"]
    mock_get_bot.handle.assert_called_once_with("invalid", None)


def test_bot_sync_project(mock_get_bot):
    """Test bot sync project command."""
    from app.bot.google_drive_bot import app
    
    client = TestClient(app)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = os.path.join(tmpdir, "manuscript.md")
        with open(test_file, 'w') as f:
            f.write("# Test Manuscript")
        
        response = client.post("/bot/command", json={
            "command": "sync",
            "args": {"project": "Test Book", "path": tmpdir}
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["project"] == "Test Project"
        assert data["uploaded_count"] == 1


def test_bot_drive_bot_class():
    """Test DriveBot class initialization."""
    from app.bot.google_drive_bot import DriveBot
    
    with patch('app.bot.google_drive_bot.googleapiclient.discovery.build') as mock_build:
        with patch('app.bot.google_drive_bot.InstalledAppFlow') as mock_flow:
            with patch('app.bot.google_drive_bot.Credentials') as mock_creds:
                mock_service = MagicMock()
                mock_build.return_value = mock_service
                
                mock_flow_instance = MagicMock()
                mock_flow.from_client_secrets_file.return_value = mock_flow_instance
                mock_flow_instance.run_local_server.return_value = MagicMock()
                
                mock_creds.from_authorized_user_file.return_value = None
                
                bot = DriveBot()
                assert bot.service == mock_service
                assert bot.running == False
                assert bot.watch_interval == 30


def test_bot_commands_handler():
    """Test BotCommands handler."""
    from app.bot.google_drive_bot import BotCommands
    
    # Create a mock bot
    mock_bot = MagicMock()
    cmds = BotCommands(mock_bot)
    
    # Test health command
    result = cmds.handle('health')
    assert result['status'] == 'healthy'
    mock_bot.last_check = None
    
    # Test help command
    result = cmds.handle('help')
    assert result['status'] == 'success'
    assert 'commands' in result
    
    # Test unknown command
    result = cmds.handle('invalid')
    assert result['status'] == 'error'
    assert 'Unknown command' in result['message']
    
    # Test case insensitivity
    result = cmds.handle('HEALTH')
    assert result['status'] == 'healthy'