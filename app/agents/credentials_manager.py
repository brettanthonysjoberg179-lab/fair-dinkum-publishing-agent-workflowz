from .base import BaseAgent
import json
import os

class CredentialsManagerAgent(BaseAgent):
    """
    The CredentialsManagerAgent assists the user in setting up the required
    JSON credential files for external APIs (like Google Drive).
    Since secrets cannot be generated programmatically via API, this agent
    handles the formatting, validation, and local persistence of provided secrets.
    """
    def __init__(self, project_id):
        super().__init__(project_id)

    def execute(self, action='guide', credentials_data=None, file_path='credentials.json'):
        """
        Actions:
        - 'guide': Returns step-by-step instructions on how to get credentials from the console.
        - 'create': Takes credentials_data and writes the formatted JSON file.
        - 'verify': Checks if the credential file exists and is valid.
        - 'reset': Deletes the token.json to force re-authentication.
        """
        if action == 'guide':
            return self._provide_guide()
        
        elif action == 'create':
            return self._create_credentials(credentials_data, file_path)
            
        elif action == 'verify':
            return self._verify_credentials(file_path)
            
        elif action == 'reset':
            return self._reset_tokens()
            
        else:
            return {'status': 'error', 'message': f'Unknown action: {action}'}

    def _provide_guide(self):
        guide = (
            "--- GOOGLE CLOUD CREDENTIALS GUIDE ---\n"
            "1. Go to: https://console.cloud.google.com/\n"
            "2. Create a project named 'Fair Dinkum Publishing'.\n"
            "3. Navigate to 'APIs & Services' -> 'Library' and Enable 'Google Drive API'.\n"
            "4. Go to 'OAuth consent screen', configure it as 'External', and add yourself as a Test User.\n"
            "5. Go to 'Credentials' -> 'Create Credentials' -> 'OAuth client ID'.\n"
            "6. Select 'Desktop App'.\n"
            "7. Download the JSON file or copy the Client ID and Client Secret.\n"
            "--------------------------------------"
        )
        return {'status': 'success', 'guide': guide}

    def _create_credentials(self, data, path):
        if not data or 'client_id' not in data or 'client_secret' not in data:
            return {'status': 'error', 'message': 'Missing client_id or client_secret in credentials_data.'}
        
        # Google's expected format for Desktop Apps
        credentials_structure = {
            "installed": {
                "client_id": data['client_id'],
                "client_secret": data['client_secret'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_id_installed": data['client_id'],
                "auth_uri_installed": "https://accounts.google.com/o/oauth2/auth",
                "token_uri_installed": "https://oauth2.googleapis.com/token"
            }
        }
        
        try:
            with open(path, 'w') as f:
                json.dump(credentials_structure, f, indent=4)
            return {'status': 'success', 'message': f'Credentials written to {path}'}
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to write file: {str(e)}'}

    def _verify_credentials(self, path):
        if not os.path.exists(path):
            return {'status': 'error', 'message': f'File {path} not found.'}
        
        try:
            with open(path, 'r') as f:
                json.load(f)
            return {'status': 'success', 'message': f'Credentials file {path} is valid JSON.'}
        except Exception as e:
            return {'status': 'error', 'message': f'Invalid JSON in {path}: {str(e)}'}

    def _reset_tokens(self):
        token_path = 'token.json'
        try:
            if os.path.exists(token_path):
                os.remove(token_path)
                return {'status': 'success', 'message': 'token.json deleted. Re-authentication required.'}
            return {'status': 'info', 'message': 'No token.json found to reset.'}
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to reset tokens: {str(e)}'}
