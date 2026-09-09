#!/usr/bin/env python3
"""
Google Drive MCP Server for Fair Dinkum Publishing.

Provides Google Drive API integration via MCP protocol.
Supports file operations, folder management, and project backup.

Usage:
    uvicorn app.mcp.google_drive_mcp_server:app --host 127.0.0.1 --port 8001
    
Environment:
    GOOGLE_CREDENTIALS_PATH: ./credentials.json
    GOOGLE_TOKEN_PATH: ./token.json
    GOOGLE_DRIVE_FOLDER_NAME: Fair Dinkum Publishing
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import io
import json

app = FastAPI(
    title="Google Drive MCP Server",
    description="MCP Server for Google Drive integration - Fair Dinkum Publishing",
    version="1.0.0"
)

# Request/Response Models
class UploadFileRequest(BaseModel):
    file_path: str
    folder_id: Optional[str] = None
    name: Optional[str] = None

class CreateFolderRequest(BaseModel):
    name: str
    parent_id: Optional[str] = None

class ProjectSyncRequest(BaseModel):
    name: str
    file_paths: List[str]
    project_folder: Optional[str] = None

class DeleteFileRequest(BaseModel):
    file_id: str

class ShareFileRequest(BaseModel):
    file_id: str
    email: str
    role: str = "reader"

# Google Drive service (lazy initialization)
_drive_service = None

def _get_drive_service():
    """Get or initialize Google Drive service."""
    global _drive_service
    if _drive_service is None:
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
            
            _drive_service = build('drive', 'v3', credentials=creds)
        except ImportError as e:
            raise RuntimeError(f"Google API libraries not installed: {e}. Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
    return _drive_service


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "google-drive-mcp"}


@app.post("/files/upload")
def upload_file(request: UploadFileRequest):
    """Upload a file to Google Drive."""
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    
    try:
        from googleapiclient.http import MediaFileUpload
        
        service = _get_drive_service()
        file_metadata = {'name': request.name or os.path.basename(request.file_path)}
        if request.folder_id:
            file_metadata['parents'] = [request.folder_id]
        
        media = MediaFileUpload(request.file_path, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType, size, webViewLink'
        ).execute()
        
        return {"status": "success", "file": file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files/list")
def list_files(query: Optional[str] = None, page_size: int = 100):
    """List files in Google Drive."""
    try:
        service = _get_drive_service()
        results = service.files().list(
            q=query,
            pageSize=page_size,
            fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, webViewLink)"
        ).execute()
        
        return {"status": "success", "files": results.get('files', [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/folders/create")
def create_folder(request: CreateFolderRequest):
    """Create a folder in Google Drive."""
    try:
        service = _get_drive_service()
        file_metadata = {
            'name': request.name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if request.parent_id:
            file_metadata['parents'] = [request.parent_id]
        
        folder = service.files().create(
            body=file_metadata,
            fields='id, name, webViewLink'
        ).execute()
        
        return {"status": "success", "folder": folder}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files/{file_id}")
def get_file(file_id: str):
    """Get file metadata."""
    try:
        service = _get_drive_service()
        file = service.files().get(
            fileId=file_id,
            fields='id, name, mimeType, size, modifiedTime, webViewLink, owners'
        ).execute()
        return {"status": "success", "file": file}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/files/delete")
def delete_file(request: DeleteFileRequest):
    """Delete a file from Google Drive."""
    try:
        service = _get_drive_service()
        service.files().delete(fileId=request.file_id).execute()
        return {"status": "success", "message": f"File {request.file_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/files/share")
def share_file(request: ShareFileRequest):
    """Share a file with a user."""
    try:
        service = _get_drive_service()
        permission = {
            'type': 'user',
            'role': request.role,
            'emailAddress': request.email
        }
        result = service.permissions().create(
            fileId=request.file_id,
            body=permission,
            sendNotificationEmail=True
        ).execute()
        return {"status": "success", "permission": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/project-sync")
def sync_project(request: ProjectSyncRequest):
    """Sync a project's files to Google Drive."""
    try:
        service = _get_drive_service()
        
        # Create project folder
        folder_metadata = {
            'name': request.name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if request.project_folder:
            folder_metadata['parents'] = [request.project_folder]
        
        folder = service.files().create(
            body=folder_metadata,
            fields='id, name'
        ).execute()
        
        uploaded = []
        for file_path in request.file_paths:
            if os.path.exists(file_path):
                from googleapiclient.http import MediaFileUpload
                file_metadata = {'name': os.path.basename(file_path), 'parents': [folder['id']]}
                media = MediaFileUpload(file_path, resumable=True)
                f = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id, name'
                ).execute()
                uploaded.append(f)
        
        return {"status": "success", "folder_id": folder['id'], "uploaded_count": len(uploaded), "files": uploaded}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# MCP Protocol endpoints
@app.post("/mcp/tools/list")
def list_tools():
    """List available MCP tools."""
    return {
        "tools": [
            {
                "name": "upload_file",
                "description": "Upload a file to Google Drive",
                "properties": {
                    "file_path": {"type": "string", "description": "Local path to file"},
                    "folder_id": {"type": "string", "description": "Target folder ID (optional)"},
                    "name": {"type": "string", "description": "File name in Drive (optional)"}
                },
                "required": ["file_path"]
            },
            {
                "name": "create_folder",
                "description": "Create a folder in Google Drive",
                "properties": {
                    "name": {"type": "string", "description": "Folder name"},
                    "parent_id": {"type": "string", "description": "Parent folder ID (optional)"}
                },
                "required": ["name"]
            },
            {
                "name": "list_files",
                "description": "List files in Google Drive",
                "properties": {
                    "query": {"type": "string", "description": "Search query (optional)"},
                    "page_size": {"type": "integer", "default": 100}
                }
            },
            {
                "name": "project_sync",
                "description": "Sync project files to Google Drive",
                "properties": {
                    "name": {"type": "string", "description": "Project name/folder name"},
                    "file_paths": {"type": "array", "items": {"type": "string"}, "description": "List of file paths to sync"},
                    "project_folder": {"type": "string", "description": "Parent folder ID (optional)"}
                },
                "required": ["name", "file_paths"]
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)