#!/usr/bin/env python3
"""
Google Drive Bot for Fair Dinkum Publishing.

Features:
- Watch for file changes in Google Drive
- Auto-organize project folders
- Sync project artifacts
- Respond to simple commands

Usage:
    python app/bot/google_drive_bot.py
    python app/bot/google_drive_bot.py --watch
    python app/bot/google_drive_bot.py --sync-project "My Book"
"""
import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('google-drive-bot')

app = FastAPI(title="Google Drive Bot", version="1.0.0")


class CommandRequest(BaseModel):
    command: str
    args: Optional[Dict[str, Any]] = None


# Lazy bot initialization
_bot = None
_commands = None


def get_bot():
    """Get or create the bot instance."""
    global _bot, _commands
    if _bot is None:
        _bot = DriveBot()
        _commands = BotCommands(_bot)
    return _bot, _commands


# Bot state
class DriveBot:
    """Google Drive Bot for Fair Dinkum Publishing."""
    
    def __init__(self):
        self.service = None
        self.watch_interval = 30  # seconds
        self.running = False
        self.last_check = None
        self.known_files = set()
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            
            credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', '../credentials.json')
            token_path = os.getenv('GOOGLE_TOKEN_PATH', '../token.json')
            scopes = ['https://www.googleapis.com/auth/drive.file']
            
            creds = None
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, scopes)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
                    creds = flow.run_local_server(port=0)
                
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Authenticated with Google Drive")
        except ImportError as e:
            logger.error(f"Google API libraries not installed: {e}")
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    def list_files(self, query: str = None, page_size: int = 100) -> List[Dict]:
        """List files from Google Drive."""
        try:
            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, mimeType, size, modifiedTime, parents)"
            ).execute()
            return results.get('files', [])
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def get_file(self, file_id: str) -> Optional[Dict]:
        """Get file metadata."""
        try:
            return self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, size, modifiedTime, parents, webViewLink'
            ).execute()
        except Exception as e:
            logger.error(f"Error getting file {file_id}: {e}")
            return None
    
    def create_folder(self, name: str, parent_id: str = None) -> Optional[str]:
        """Create a folder in Google Drive."""
        try:
            metadata = {'name': name, 'mimeType': 'application/vnd.google-apps.folder'}
            if parent_id:
                metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            logger.info(f"Created folder: {name} ({folder.get('id')})")
            return folder.get('id')
        except Exception as e:
            logger.error(f"Error creating folder {name}: {e}")
            return None
    
    def find_or_create_folder(self, name: str, parent_id: str = None) -> Optional[str]:
        """Find existing folder or create it."""
        # Search for existing folder
        query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        files = self.list_files(query=query, page_size=1)
        if files:
            return files[0]['id']
        
        return self.create_folder(name, parent_id)
    
    def sync_project_folder(self, project_name: str, local_path: str) -> Dict[str, Any]:
        """
        Sync a project folder to Google Drive.
        Creates folder structure and uploads files.
        """
        try:
            # Find or create main project folder
            parent_folder_id = self.find_or_create_folder("Fair Dinkum Publishing")
            project_folder_id = self.find_or_create_folder(project_name, parent_folder_id)
            
            # Create subfolders
            subfolders = ['manuscripts', 'covers', 'output', 'research', 'sales']
            folder_ids = {}
            for subfolder in subfolders:
                folder_id = self.find_or_create_folder(subfolder, project_folder_id)
                folder_ids[subfolder] = folder_id
            
            # Upload files from local path
            uploaded = []
            local_path = Path(local_path)
            if local_path.exists():
                for file_path in local_path.rglob('*'):
                    if file_path.is_file():
                        # Determine which subfolder based on file type/location
                        relative = file_path.relative_to(local_path)
                        target_folder = project_folder_id
                        
                        # Simple routing logic
                        if 'cover' in str(relative).lower() or 'cover' in str(file_path).lower():
                            target_folder = folder_ids.get('covers', project_folder_id)
                        elif any(ext in str(file_path).lower() for ext in ['.epub', '.pdf', '.mobi']):
                            target_folder = folder_ids.get('output', project_folder_id)
                        elif 'research' in str(relative).lower():
                            target_folder = folder_ids.get('research', project_folder_id)
                        
                        # Upload file
                        file_id = self._upload_file(str(file_path), target_folder)
                        if file_id:
                            uploaded.append({
                                'local': str(relative),
                                'drive_id': file_id,
                                'folder': target_folder
                            })
            
            return {
                'status': 'success',
                'project': project_name,
                'project_folder_id': project_folder_id,
                'uploaded_count': len(uploaded),
                'files': uploaded
            }
        except Exception as e:
            logger.error(f"Error syncing project {project_name}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _upload_file(self, file_path: str, folder_id: str) -> Optional[str]:
        """Upload a file to a specific folder."""
        try:
            from googleapiclient.http import MediaFileUpload
            
            file_metadata = {
                'name': os.path.basename(file_path),
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            logger.info(f"Uploaded: {file_path} -> {file.get('id')}")
            return file.get('id')
        except Exception as e:
            logger.error(f"Error uploading {file_path}: {e}")
            return None
    
    def watch_for_changes(self, callback=None):
        """
        Watch for file changes in Google Drive.
        Uses polling since Drive API doesn't have native webhooks for all changes.
        """
        logger.info(f"Starting watch mode (checking every {self.watch_interval}s)")
        self.running = True
        
        # Initial scan
        files = self.list_files()
        self.known_files = {f['id'] for f in files}
        self.last_check = datetime.now()
        logger.info(f"Initial scan: {len(self.known_files)} files")
        
        while self.running:
            try:
                time.sleep(self.watch_interval)
                
                # Check for changes
                files = self.list_files()
                current_ids = {f['id'] for f in files}
                
                # New files
                new_files = current_ids - self.known_files
                if new_files:
                    for f in files:
                        if f['id'] in new_files:
                            logger.info(f"NEW FILE: {f['name']} ({f['mimeType']})")
                            if callback:
                                callback('created', f)
                
                # Deleted files
                deleted = self.known_files - current_ids
                if deleted:
                    logger.info(f"DELETED: {len(deleted)} files")
                
                # Modified files (check timestamps)
                modified = []
                old_map = {f['id']: f for f in files if f['id'] in self.known_files}
                for f in files:
                    if f['id'] in old_map:
                        old_time = old_map[f['id']].get('modifiedTime', '')
                        new_time = f.get('modifiedTime', '')
                        if old_time != new_time:
                            modified.append(f)
                            logger.info(f"MODIFIED: {f['name']}")
                
                if modified and callback:
                    for f in modified:
                        callback('modified', f)
                
                self.known_files = current_ids
                self.last_check = datetime.now()
                
            except KeyboardInterrupt:
                logger.info("Watch stopped by user")
                break
            except Exception as e:
                logger.error(f"Watch error: {e}")
                time.sleep(self.watch_interval)
    
    def stop_watch(self):
        """Stop watching for changes."""
        self.running = False
        logger.info("Stopping watch mode...")


# Bot commands
class BotCommands:
    """Command handlers for the Drive Bot."""
    
    def __init__(self, bot: DriveBot):
        self.bot = bot
    
    def handle(self, command: str, args: Dict = None) -> Dict[str, Any]:
        """Route and execute commands."""
        args = args or {}
        
        commands = {
            'list': self.cmd_list,
            'info': self.cmd_info,
            'create-folder': self.cmd_create_folder,
            'sync': self.cmd_sync,
            'search': self.cmd_search,
            'health': self.cmd_health,
            'help': self.cmd_help,
        }
        
        handler = commands.get(command.lower())
        if not handler:
            return {
                'status': 'error',
                'message': f"Unknown command: {command}. Type 'help' for available commands."
            }
        
        try:
            return handler(args)
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def cmd_list(self, args: Dict) -> Dict:
        """List files."""
        query = args.get('query')
        files = self.bot.list_files(query=query)
        return {
            'status': 'success',
            'count': len(files),
            'files': files
        }
    
    def cmd_info(self, args: Dict) -> Dict:
        """Get file info."""
        file_id = args.get('file_id')
        if not file_id:
            return {'status': 'error', 'message': 'file_id required'}
        
        file = self.bot.get_file(file_id)
        if file:
            return {'status': 'success', 'file': file}
        return {'status': 'error', 'message': 'File not found'}
    
    def cmd_create_folder(self, args: Dict) -> Dict:
        """Create a folder."""
        name = args.get('name')
        parent_id = args.get('parent_id')
        
        if not name:
            return {'status': 'error', 'message': 'name required'}
        
        folder_id = self.bot.find_or_create_folder(name, parent_id)
        if folder_id:
            return {
                'status': 'success',
                'folder_id': folder_id,
                'name': name
            }
        return {'status': 'error', 'message': 'Failed to create folder'}
    
    def cmd_sync(self, args: Dict) -> Dict:
        """Sync a project folder."""
        project_name = args.get('project')
        local_path = args.get('path', '.')
        
        if not project_name:
            return {'status': 'error', 'message': 'project name required'}
        
        return self.bot.sync_project_folder(project_name, local_path)
    
    def cmd_search(self, args: Dict) -> Dict:
        """Search files."""
        query = args.get('query')
        if not query:
            return {'status': 'error', 'message': 'query required'}
        
        files = self.bot.list_files(query=query)
        return {
            'status': 'success',
            'count': len(files),
            'files': files
        }
    
    def cmd_health(self, args: Dict) -> Dict:
        """Health check."""
        return {
            'status': 'healthy',
            'service': 'google-drive-bot',
            'last_check': self.bot.last_check.isoformat() if self.bot.last_check else None
        }
    
    def cmd_help(self, args: Dict) -> Dict:
        """Show available commands."""
        return {
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


# FastAPI endpoints
@app.get("/health")
def health():
    """Health check."""
    _, commands = get_bot()
    return commands.cmd_health({})


@app.post("/bot/command")
def execute_command(request: CommandRequest):
    """Execute a bot command."""
    _, commands = get_bot()
    result = commands.handle(request.command, request.args)
    return JSONResponse(content=result)


@app.get("/bot/commands")
def list_commands():
    """List available commands."""
    _, commands = get_bot()
    return commands.cmd_help({})


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='Google Drive Bot for Fair Dinkum Publishing')
    parser.add_argument('--watch', action='store_true', help='Watch for file changes')
    parser.add_argument('--sync-project', type=str, help='Sync a project folder')
    parser.add_argument('--path', type=str, default='.', help='Local path for sync')
    parser.add_argument('--port', type=int, default=8002, help='API server port')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='API server host')
    
    args = parser.parse_args()
    
    # Initialize bot for CLI modes
    bot, commands = get_bot()
    
    if args.watch:
        # Watch mode
        def on_change(event_type, file_info):
            logger.info(f"[{event_type.upper()}] {file_info.get('name')}")
        
        try:
            bot.watch_for_changes(callback=on_change)
        except KeyboardInterrupt:
            bot.stop_watch()
    
    elif args.sync_project:
        # Sync mode
        logger.info(f"Syncing project: {args.sync_project}")
        result = bot.sync_project_folder(args.sync_project, args.path)
        print(json.dumps(result, indent=2))
    
    else:
        # API server mode
        logger.info(f"Starting Google Drive Bot API server on {args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()