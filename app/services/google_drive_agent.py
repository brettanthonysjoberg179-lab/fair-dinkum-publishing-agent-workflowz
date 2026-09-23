"""Google Drive Agent — powered by Composio CLI.

This service wraps Composio's Google Drive toolkit to provide:
- File/folder CRUD operations
- Project folder management
- Artifact sync
- Intelligent search and organization

Uses subprocess to call the `composio` CLI which is already authenticated.

Usage:
    from app.services.google_drive_agent import GoogleDriveService
    svc = GoogleDriveService()
    files = svc.list_files()
    folder = svc.create_folder("My Project")
"""
import os
import json
import logging
import subprocess
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Composio CLI tool slugs (verified via `composio connections list`)
TOOL_CREATE_FOLDER = "GOOGLEDRIVE_CREATE_FOLDER"
TOOL_LIST_FILES = "GOOGLEDRIVE_LIST_FILES"
TOOL_FIND_FILE = "GOOGLEDRIVE_FIND_FILE"
TOOL_CREATE_FILE = "GOOGLEDRIVE_CREATE_FILE"
TOOL_CREATE_FILE_FROM_TEXT = "GOOGLEDRIVE_CREATE_FILE_FROM_TEXT"
TOOL_GET_FILE_METADATA = "GOOGLEDRIVE_GET_FILE_METADATA"
TOOL_DELETE_FILE = "GOOGLEDRIVE_GOOGLE_DRIVE_DELETE_FOLDER_OR_FILE_ACTION"
TOOL_UPLOAD_FILE = "GOOGLEDRIVE_UPLOAD_FILE"
TOOL_LIST_CHILDREN = "GOOGLEDRIVE_LIST_CHILDREN_V2"

FD_ROOT_FOLDER = "Fair Dinkum Publishing"


class GoogleDriveService:
    """Google Drive operations via Composio CLI."""

    def __init__(self):
        self._connected = False
        self._check_connection()

    def _check_connection(self):
        """Check if Composio CLI is available and authenticated."""
        try:
            result = subprocess.run(
                ["/home/brettanthonysjoberg179/.local/bin/composio", "connections"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                googledrive = data.get("googledrive", [])
                self._connected = any(c.get("status") == "ACTIVE" for c in googledrive)
                if self._connected:
                    logger.info("Composio CLI connected (googledrive ACTIVE)")
                else:
                    logger.warning("Google Drive connection not ACTIVE")
            else:
                logger.error(f"Composio connections failed: {result.stderr[:500]}")
        except Exception as e:
            logger.error(f"Composio check failed: {e}")

    def _execute_tool(self, tool_slug: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Composio tool via CLI and return parsed result."""
        if not self._connected:
            return {"status": "error", "message": "Composio not connected"}

        try:
            cmd = ["/home/brettanthonysjoberg179/.local/bin/composio", "execute", f'"{tool_slug}"', "-d", json.dumps(params)]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout) if result.stdout.strip() else {}
                    # Composio wraps response: {"successful": true, "data": {...}, "error": null}
                    if response.get("successful"):
                        return {"status": "success", "data": response.get("data", {})}
                    else:
                        return {"status": "error", "message": response.get("error", "Unknown error")}
                except json.JSONDecodeError:
                    return {"status": "success", "data": result.stdout}
            else:
                logger.error(f"Tool {tool_slug} failed: {result.stderr[:500]}")
                return {"status": "error", "message": result.stderr[:500]}
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Tool execution timed out"}
        except Exception as e:
            logger.error(f"Tool {tool_slug} error: {e}")
            return {"status": "error", "message": str(e)}

    def is_connected(self) -> bool:
        return self._connected

    # ── Folder Operations ──────────────────────────────────────────────────

    def get_or_create_root_folder(self) -> Optional[str]:
        """Get or create the 'Fair Dinkum Publishing' root folder."""
        result = self._execute_tool(TOOL_FIND_FILE, {
            "q": f"name='{FD_ROOT_FOLDER}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        })
        if result["status"] == "success":
            data = result["data"]
            if isinstance(data, dict) and "files" in data:
                files = data["files"]
                if files:
                    return files[0]["id"]
        return self.create_folder(FD_ROOT_FOLDER)

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Create a folder in Google Drive. Returns folder ID."""
        params = {"name": name}
        if parent_id:
            params["parent_id"] = parent_id
        result = self._execute_tool(TOOL_CREATE_FOLDER, params)
        if result["status"] == "success":
            data = result["data"]
            folder_id = data.get("id") if isinstance(data, dict) else None
            logger.info(f"Created folder '{name}' (ID: {folder_id})")
            return folder_id
        logger.error(f"Failed to create folder '{name}': {result}")
        return None

    def find_folder(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a folder by exact name."""
        result = self._execute_tool(TOOL_FIND_FILE, {
            "q": f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        })
        if result["status"] == "success":
            data = result["data"]
            if isinstance(data, dict) and "files" in data:
                files = data["files"]
                return files[0] if files else None
        return None

    # ── File Operations ───────────────────────────────────────────────────

    def list_files(
        self,
        query: Optional[str] = None,
        fields: str = "id,name,mimeType,size,modifiedTime,webViewLink,parents",
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """List files from Google Drive."""
        params = {"fields": fields, "pageSize": page_size}
        if query:
            params["q"] = query
        result = self._execute_tool(TOOL_LIST_FILES, params)
        if result["status"] == "success":
            data = result["data"]
            if isinstance(data, dict) and "files" in data:
                return data["files"]
        logger.error(f"Failed to list files: {result}")
        return []

    def find_file(self, name: Optional[str] = None, mime_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find a file by name or MIME type."""
        parts = ["trashed=false"]
        if name:
            parts.append(f"name='{name}'")
        if mime_type:
            parts.append(f"mimeType='{mime_type}'")
        q = " and ".join(parts)
        result = self._execute_tool(TOOL_FIND_FILE, {"q": q})
        if result["status"] == "success":
            data = result["data"]
            if isinstance(data, dict) and "files" in data:
                files = data["files"]
                return files[0] if files else None
        return None

    def list_children(self, folder_id: str, fields: str = "id,name,mimeType,size,modifiedTime") -> List[Dict[str, Any]]:
        """List children of a folder."""
        result = self._execute_tool(TOOL_LIST_CHILDREN, {
            "folderId": folder_id,
            "fields": fields,
        })
        if result["status"] == "success":
            data = result["data"]
            if isinstance(data, dict) and "files" in data:
                return data["files"]
        return []

    def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific file."""
        result = self._execute_tool(TOOL_GET_FILE_METADATA, {"fileId": file_id})
        if result["status"] == "success":
            return result["data"] if isinstance(result["data"], dict) else None
        return None

    def create_file_from_text(
        self,
        file_name: str,
        text_content: str,
        mime_type: str = "text/plain",
        parent_id: Optional[str] = None,
    ) -> Optional[str]:
        """Create a new file from text content. Returns file ID."""
        params = {
            "file_name": file_name,
            "text_content": text_content,
            "mime_type": mime_type,
        }
        if parent_id:
            params["parent_id"] = parent_id
        result = self._execute_tool(TOOL_CREATE_FILE_FROM_TEXT, params)
        if result["status"] == "success":
            data = result["data"]
            file_id = data.get("id") if isinstance(data, dict) else None
            logger.info(f"Created file '{file_name}' (ID: {file_id})")
            return file_id
        logger.error(f"Failed to create file '{file_name}': {result}")
        return None

    def upload_file(self, file_path: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Upload a local file to Google Drive. Returns file ID."""
        from pathlib import Path
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        mime_types = {
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".html": "text/html",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".epub": "application/epub+zip",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".zip": "application/zip",
            ".json": "application/json",
            ".csv": "text/csv",
        }

        params = {
            "file_to_upload": {
                "name": path.name,
                "mimetype": mime_types.get(path.suffix, "application/octet-stream"),
                "file_path": str(path.absolute()),
            }
        }
        if parent_id:
            params["parent_id"] = parent_id

        result = self._execute_tool(TOOL_UPLOAD_FILE, params)
        if result["status"] == "success":
            data = result["data"]
            file_id = data.get("id") if isinstance(data, dict) else None
            logger.info(f"Uploaded '{path.name}' (ID: {file_id})")
            return file_id
        logger.error(f"Failed to upload '{path.name}': {result}")
        return None

    def delete_file(self, file_id: str, supports_all_drives: bool = True) -> bool:
        """Delete a file or folder from Google Drive."""
        result = self._execute_tool(TOOL_DELETE_FILE, {
            "fileId": file_id,
            "supportsAllDrives": supports_all_drives,
        })
        if result["status"] == "success":
            logger.info(f"Deleted file/folder (ID: {file_id})")
            return True
        logger.error(f"Failed to delete '{file_id}': {result}")
        return False

    # ── Project Workflows ─────────────────────────────────────────────────

    def sync_project(self, project_name: str, local_path: str) -> Dict[str, Any]:
        """Sync a local project folder to Google Drive."""
        from pathlib import Path
        local = Path(local_path)
        if not local.exists():
            return {"status": "error", "message": f"Path not found: {local_path}"}

        root_id = self.get_or_create_root_folder()
        project_folder = self.find_folder(project_name)
        if project_folder:
            project_id = project_folder["id"]
        else:
            project_id = self.create_folder(project_name, parent_id=root_id)

        if not project_id:
            return {"status": "error", "message": f"Could not create folder for {project_name}"}

        results = []
        for file_path in local.rglob("*"):
            if file_path.is_file():
                rel = file_path.relative_to(local)
                parent = project_id
                parts = rel.parts[:-1]
                for part in parts:
                    existing = self.find_folder(part)
                    if existing:
                        parent = existing["id"]
                    else:
                        new_id = self.create_folder(part, parent_id=parent)
                        parent = new_id or parent

                drive_id = self.upload_file(str(file_path), parent_id=parent)
                results.append({
                    "local": str(rel),
                    "drive_id": drive_id,
                    "status": "uploaded" if drive_id else "failed",
                })

        return {
            "status": "success",
            "project": project_name,
            "folder_id": project_id,
            "total_files": len(results),
            "uploaded": sum(1 for r in results if r["status"] == "uploaded"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "files": results,
        }

    def get_drive_stats(self) -> Dict[str, Any]:
        """Get overall Drive usage stats."""
        files = self.list_files(page_size=1000)
        total_size = sum(int(f.get("size", 0) or 0) for f in files)
        folders = [f for f in files if f.get("mimeType") == "application/vnd.google-apps.folder"]
        return {
            "total_files": len(files),
            "total_folders": len(folders),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "root_folder_exists": self.find_folder(FD_ROOT_FOLDER) is not None,
        }

    def search_files(self, query: str) -> List[Dict[str, Any]]:
        """Search files by name or content."""
        return self.list_files(query=f"fullText contains '{query}' and trashed=false")


def get_drive_service() -> GoogleDriveService:
    """Factory function for lazy initialization."""
    return GoogleDriveService()


if __name__ == "__main__":
    svc = GoogleDriveService()
    print(f"Connected: {svc.is_connected()}")
    if svc.is_connected():
        stats = svc.get_drive_stats()
        print(json.dumps(stats, indent=2))
