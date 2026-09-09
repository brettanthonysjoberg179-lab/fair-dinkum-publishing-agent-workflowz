import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class GoogleDriveService:
    """
    Service to handle interaction with Google Drive API.
    """
    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        if not creds or not creds.valid:
            # In a real production environment, this would be handled via a 
            # redirect URI and a web-based OAuth flow.
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, self.SCOPES
            )
            creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build('drive', 'v3', credentials=creds)

    def upload_file(self, file_path, folder_id=None, filename=None):
        """
        Uploads a file to Google Drive.
        """
        name = filename or os.path.basename(file_path)
        file_metadata = {'name': name}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id'
        ).execute()
        
        return file.get('id')

    def create_folder(self, folder_name, parent_id=None):
        """
        Creates a folder in Google Drive.
        """
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
            
        folder = self.service.files().create(
            body=file_metadata, 
            fields='id'
        ).execute()
        
        return folder.get('id')

    def list_files(self, query=None):
        """
        Lists files in Google Drive.
        """
        results = self.service.files().list(
            q=query, 
            fields="nextPageToken, files(id, name)"
        ).execute()
        return results.get('files', [])
