from .base import BaseAgent
from ..services.google_drive import GoogleDriveService
import os

class CloudArchivistAgent(BaseAgent):
    """
    The CloudArchivistAgent is responsible for syncing project artifacts, 
    manuscripts, and research notes to Google Drive for backup and collaboration.
    """
    def __init__(self, project_id):
        super().__init__(project_id)
        self.drive_service = None

    def _initialize_service(self):
        if not self.drive_service:
            # paths would ideally be loaded from config/env
            self.drive_service = GoogleDriveService(
                credentials_path='credentials.json', 
                token_path='token.json'
            )

    def execute(self, artifact_paths=None, project_name="Fair Dinkum Project"):
        self.update_status('Initializing Cloud Sync')
        
        if not artifact_paths:
            return {
                'status': 'error',
                'message': 'No artifact paths provided for synchronization.'
            }

        try:
            self._initialize_service()
            
            # 1. Create a project-specific folder on Drive
            project_folder_id = self.drive_service.create_folder(project_name)
            self.update_status(f'Created project folder: {project_name}')
            
            uploaded_files = []
            for path in artifact_paths:
                if os.path.exists(path):
                    file_id = self.drive_service.upload_file(
                        file_path=path, 
                        folder_id=project_folder_id
                    )
                    uploaded_files.append({'path': path, 'drive_id': file_id})
            
            self.update_status('Synchronization complete')
            return {
                'status': 'success',
                'project_folder_id': project_folder_id,
                'uploaded_files': uploaded_files
            }

        except Exception as e:
            self.update_status('Synchronization failed')
            return {
                'status': 'error',
                'message': str(e)
            }
