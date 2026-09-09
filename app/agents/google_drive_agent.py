#!/usr/bin/env python3
"""
Google Drive Agent with Ollama LLM Integration for Fair Dinkum Publishing.

Features:
- Google Drive file management with AI-powered analysis
- Local LLM inference via Ollama
- Intelligent file organization and tagging
- Content analysis and summarization
- Project-aware workflows

Usage:
    python app/agents/google_drive_agent.py
    uvicorn app.agents.google_drive_agent:app --port 8003
    
Environment:
    GOOGLE_CREDENTIALS_PATH: ./credentials.json
    GOOGLE_TOKEN_PATH: ./token.json
    OLLAMA_BASE_URL: http://localhost:11434
    OLLAMA_MODEL: llama3.2:latest
"""
import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('google-drive-agent')

app = FastAPI(title="Google Drive Agent", version="1.0.0")


# Request/Response Models
class AnalyzeFileRequest(BaseModel):
    file_id: str
    analysis_type: str = "summary"  # summary, tags, classification

class OrganizeRequest(BaseModel):
    query: str = None
    auto_organize: bool = False

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ProjectSyncRequest(BaseModel):
    project_name: str
    local_path: str
    analyze: bool = True


class OllamaClient:
    """Client for Ollama LLM inference."""
    
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = model or os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize OpenAI-compatible client for Ollama."""
        try:
            from openai import OpenAI
            self.client = OpenAI(
                base_url=f"{self.base_url}/v1",
                api_key="ollama"
            )
            logger.info(f"Ollama client initialized: {self.base_url} model={self.model}")
        except ImportError:
            logger.warning("openai package not installed; falling back to requests")
            self.client = None
    
    def chat(self, messages: List[Dict], temperature: float = 0.7) -> Optional[str]:
        """Send chat completion request."""
        try:
            if self.client:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature
                )
                return response.choices[0].message.content
            else:
                # Fallback to requests
                import requests
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False
                    },
                    timeout=60
                )
                if response.status_code == 200:
                    return response.json().get('message', {}).get('content')
                return None
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            return None
    
    def generate(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Generate text from prompt."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages)


class GoogleDriveAgent:
    """AI-powered Google Drive Agent with local LLM."""
    
    def __init__(self):
        self.ollama = OllamaClient()
        self.service = None
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
            logger.info("Google Drive authenticated")
        except Exception as e:
            logger.error(f"Google Drive auth failed: {e}")
            raise
    
    def list_files(self, query: str = None, page_size: int = 100) -> List[Dict]:
        """List files from Google Drive."""
        try:
            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, mimeType, size, modifiedTime, webViewLink)"
            ).execute()
            return results.get('files', [])
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def get_file_content(self, file_id: str) -> Optional[str]:
        """Get file content for analysis."""
        try:
            file = self.service.files().get(fileId=file_id).execute()
            mime_type = file.get('mimeType', '')
            
            if 'text/' in mime_type or mime_type == 'application/json':
                # Download text content
                import io
                from googleapiclient.http import MediaIoBaseDownload
                
                request = self.service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                
                fh.seek(0)
                return fh.read().decode('utf-8', errors='ignore')
            
            return f"[Binary file: {mime_type}]"
        except Exception as e:
            logger.error(f"Error getting file content: {e}")
            return None
    
    def analyze_file_with_llm(self, file_id: str, analysis_type: str = "summary") -> Dict[str, Any]:
        """Analyze a file using Ollama LLM."""
        try:
            # Get file metadata
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, size, modifiedTime, webViewLink'
            ).execute()
            
            # Get content
            content = self.get_file_content(file_id)
            if not content:
                return {
                    'status': 'error',
                    'message': 'Could not retrieve file content',
                    'file': file
                }
            
            # Create analysis prompt
            if analysis_type == "summary":
                prompt = f"""Analyze this file and provide a concise summary.
File: {file['name']}
Type: {file['mimeType']}

Content:
{content[:3000]}  # Limit context

Provide a brief summary of what this file contains."""
                system = "You are a helpful assistant that summarizes documents concisely."
            
            elif analysis_type == "tags":
                prompt = f"""Generate 5-10 relevant tags/keywords for this file.
File: {file['name']}

Content:
{content[:2000]}

Return tags as a comma-separated list."""
                system = "You are a helpful assistant that generates relevant tags for documents."
            
            elif analysis_type == "classification":
                prompt = f"""Classify this file into a category.
File: {file['name']}

Content:
{content[:2000]}

Possible categories: manuscript, research, cover, output, sales, other

Respond with just the category name."""
                system = "You are a helpful assistant that classifies documents."
            
            else:
                return {'status': 'error', 'message': f'Unknown analysis type: {analysis_type}'}
            
            # Get LLM analysis
            analysis = self.ollama.generate(prompt, system_prompt=system)
            
            return {
                'status': 'success',
                'file': file,
                'analysis_type': analysis_type,
                'analysis': analysis,
                'content_preview': content[:500] if content else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def intelligent_organize(self, query: str = None) -> Dict[str, Any]:
        """Use LLM to intelligently organize files."""
        try:
            # Get all files
            files = self.list_files()
            
            if not files:
                return {'status': 'success', 'message': 'No files to organize', 'actions': []}
            
            # Create organization prompt
            file_list = "\n".join([
                f"- {f['name']} ({f['mimeType']}, modified: {f.get('modifiedTime', 'unknown')})"
                for f in files[:50]
            ])
            
            if query:
                prompt = f"""Analyze these Google Drive files and suggest an organization plan for: {query}

Files:
{file_list}

Suggest:
1. Which files belong together
2. What folders should be created
3. How to name them

Be specific and actionable."""
            else:
                prompt = f"""Analyze these Google Drive files and suggest an organization plan.

Files:
{file_list}

Suggest:
1. logical folder groupings
2. file renaming if needed
3. priority files

Be specific and actionable."""
            
            system = """You are a file organization expert. 
Analyze file lists and provide clear, actionable organization plans.
Format your response as JSON with keys: folders (list of folder names), 
file_moves (list of {{file, folder}}), renames (list of {{old, new}})."""
            
            suggestion = self.ollama.generate(prompt, system_prompt=system)
            
            return {
                'status': 'success',
                'total_files': len(files),
                'suggestion': suggestion,
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Error organizing files: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def chat_about_drive(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """Chat with the LLM about Drive contents."""
        try:
            # Get context about Drive files
            files = self.list_files(page_size=20)
            file_context = "\n".join([
                f"- {f['name']} ({f['mimeType']})"
                for f in files
            ]) if files else "No files in Drive"
            
            system_prompt = f"""You are a helpful assistant for Fair Dinkum Publishing's Google Drive.
You have access to the following files:

{file_context}

Answer questions about files, suggest organization, help find documents, etc."""
            
            messages = []
            if context and 'history' in context:
                messages.extend(context['history'][-10:])  # Last 10 messages
            
            messages.append({"role": "user", "content": message})
            
            response = self.ollama.chat(messages, temperature=0.7)
            
            return {
                'status': 'success',
                'response': response,
                'context': {
                    'files_available': len(files),
                    'last_query': message
                }
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {'status': 'error', 'message': str(e)}


# Initialize agent
_agent = None

def get_agent():
    """Get or create agent instance."""
    global _agent
    if _agent is None:
        _agent = GoogleDriveAgent()
    return _agent


# FastAPI endpoints
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "google-drive-agent",
        "ollama": "connected" if OllamaClient().client else "fallback-mode"
    }

@app.post("/analyze")
def analyze_file(request: AnalyzeFileRequest):
    agent = get_agent()
    result = agent.analyze_file_with_llm(request.file_id, request.analysis_type)
    return JSONResponse(content=result)

@app.post("/organize")
def organize_files(request: OrganizeRequest):
    agent = get_agent()
    result = agent.intelligent_organize(request.query)
    return JSONResponse(content=result)

@app.post("/chat")
def chat(request: ChatRequest):
    agent = get_agent()
    result = agent.chat_about_drive(request.message, request.context)
    return JSONResponse(content=result)

@app.get("/files")
def get_files(query: str = None):
    agent = get_agent()
    files = agent.list_files(query=query)
    return {"status": "success", "count": len(files), "files": files}

@app.post("/sync-project")
def sync_project(request: ProjectSyncRequest):
    """Sync project with AI analysis."""
    agent = get_agent()
    
    # Create project folder
    folder_id = agent.find_or_create_folder(f"Fair Dinkum Publishing/{request.project_name}")
    
    results = []
    local_path = Path(request.local_path)
    
    if local_path.exists():
        for file_path in local_path.rglob('*'):
            if file_path.is_file():
                # Upload file
                drive_id = agent._upload_file(str(file_path), folder_id)
                
                analysis = None
                if request.analyze and drive_id:
                    # Analyze with LLM
                    analysis = agent.analyze_file_with_llm(drive_id, "tags")
                
                results.append({
                    'local': str(file_path.relative_to(local_path)),
                    'drive_id': drive_id,
                    'analysis': analysis
                })
    
    return {
        "status": "success",
        "project": request.project_name,
        "folder_id": folder_id,
        "uploaded_count": len(results),
        "files": results
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003)