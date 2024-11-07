import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock

class GoogleDriveIntegration(WorkflowBlock):
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive'
    ]
    
    @classmethod
    def register(cls, type: str):
        super(GoogleDriveIntegration, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Google Drive Integration",
                "description": "Executes various Google Drive API operations for files and folders.",
                "category": "Storage",
                "fields": {
                    "credentials_path": {
                        "name": "Credentials Path",
                        "type": "Text",
                        "description": "Path to your Google credentials JSON file"
                    },
                    "token_path": {
                        "name": "Token Path",
                        "type": "Text",
                        "description": "Path to store/retrieve the OAuth token",
                        "default": "token.json"
                    },
                    "operation": {
                        "name": "Operation",
                        "type": "Text",
                        "options": {
                            # File operations
                            "list_files": "List Files",
                            "upload_file": "Upload File",
                            "download_file": "Download File",
                            "delete_file": "Delete File",
                            "copy_file": "Copy File",
                            "move_file": "Move File",
                            "search_files": "Search Files",
                            
                            # Folder operations
                            "create_folder": "Create Folder",
                            "list_folder_contents": "List Folder Contents",
                            "delete_folder": "Delete Folder",
                            
                            # Permission operations
                            "share_file": "Share File/Folder",
                            "get_permissions": "Get Permissions",
                            "update_permissions": "Update Permissions",
                            "remove_permissions": "Remove Permissions"
                        },
                        "default": "list_files"
                    },
                    "file_path": {
                        "name": "File Path",
                        "type": "Text",
                        "description": "Local path of the file to upload/download",
                        "required": False
                    },
                    "file_id": {
                        "name": "File ID",
                        "type": "Text",
                        "description": "Google Drive file/folder ID",
                        "required": False
                    },
                    "folder_id": {
                        "name": "Folder ID",
                        "type": "Text",
                        "description": "Parent folder ID for operations",
                        "required": False
                    },
                    "name": {
                        "name": "Name",
                        "type": "Text",
                        "description": "Name for new files/folders",
                        "required": False
                    },
                    "mime_type": {
                        "name": "MIME Type",
                        "type": "Text",
                        "description": "MIME type for file operations",
                        "required": False
                    },
                    "query": {
                        "name": "Search Query",
                        "type": "Text",
                        "description": "Query string for searching files",
                        "required": False
                    },
                    "permissions": {
                        "name": "Permissions",
                        "type": "Key-Value",
                        "description": "Permissions configuration for sharing",
                        "default": "{}",
                        "required": False
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "The operation was completed successfully.",
                        "style": "success",
                    },
                    "apiError": {
                        "name": "API Error",
                        "description": "An error occurred while making the API request.",
                        "style": "error",
                    },
                    "authError": {
                        "name": "Authentication Error",
                        "description": "Authentication failed or insufficient permissions.",
                        "style": "error",
                    },
                    "fileError": {
                        "name": "File Error",
                        "description": "Error handling local files.",
                        "style": "error",
                    }
                },
            }
        ))

    def _get_credentials(self, credentials_path: str, token_path: str) -> Credentials:
        """Get or refresh credentials for Google Drive API"""
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
                
        return creds

    def _build_service(self, credentials: Credentials):
        """Build Google Drive API service"""
        return build('drive', 'v3', credentials=credentials)

    def _list_files(self, service, query: str = None, folder_id: str = None) -> Dict[str, Any]:
        """List files in Google Drive or specific folder"""
        try:
            query_parts = []
            if query:
                query_parts.append(query)
            if folder_id:
                query_parts.append(f"'{folder_id}' in parents")
            
            final_query = ' and '.join(query_parts) if query_parts else None
            
            files = []
            page_token = None
            while True:
                response = service.files().list(
                    q=final_query,
                    spaces='drive',
                    fields='nextPageToken, files(id, name, mimeType, modifiedTime, size)',
                    pageToken=page_token
                ).execute()
                
                files.extend(response.get('files', []))
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
                    
            return {"files": files}
        except Exception as e:
            self.outcome = "apiError"
            raise RuntimeError(f"Error listing files: {str(e)}")

    def _upload_file(self, service, file_path: str, folder_id: str = None, mime_type: str = None) -> Dict[str, Any]:
        """Upload a file to Google Drive"""
        try:
            file_metadata = {
                'name': os.path.basename(file_path)
            }
            if folder_id:
                file_metadata['parents'] = [folder_id]

            media = MediaFileUpload(
                file_path,
                mimetype=mime_type,
                resumable=True
            )

            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, webViewLink'
            ).execute()

            return file
        except Exception as e:
            self.outcome = "fileError"
            raise RuntimeError(f"Error uploading file: {str(e)}")

    def _download_file(self, service, file_id: str, output_path: str) -> Dict[str, Any]:
        """Download a file from Google Drive"""
        try:
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                
            fh.seek(0)
            with open(output_path, 'wb') as f:
                f.write(fh.read())
                f.close()

            return {"status": "downloaded", "path": output_path}
        except Exception as e:
            self.outcome = "fileError"
            raise RuntimeError(f"Error downloading file: {str(e)}")

    def _create_folder(self, service, name: str, parent_id: str = None) -> Dict[str, Any]:
        """Create a new folder in Google Drive"""
        try:
            file_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]

            folder = service.files().create(
                body=file_metadata,
                fields='id, name, mimeType, webViewLink'
            ).execute()

            return folder
        except Exception as e:
            self.outcome = "apiError"
            raise RuntimeError(f"Error creating folder: {str(e)}")

    def _share_file(self, service, file_id: str, permissions: Dict[str, Any]) -> Dict[str, Any]:
        """Share a file or folder with specified permissions"""
        try:
            permission = service.permissions().create(
                fileId=file_id,
                body=permissions,
                fields='id, type, role, emailAddress'
            ).execute()

            return permission
        except Exception as e:
            self.outcome = "apiError"
            raise RuntimeError(f"Error sharing file: {str(e)}")

    def run(self):
        try:
            # Get required fields
            credentials_path = self._get_field("credentials_path")
            token_path = self._get_field("token_path")
            operation = self._get_field("operation")

            # Authenticate and build service
            credentials = self._get_credentials(credentials_path, token_path)
            service = self._build_service(credentials)

            # Get optional fields
            file_path = self._get_field("file_path", True)
            file_id = self._get_field("file_id", True)
            folder_id = self._get_field("folder_id", True)
            name = self._get_field("name", True)
            mime_type = self._get_field("mime_type", True)
            query = self._get_field("query", True)
            permissions = self._get_field("permissions", True, "{}")

            # Execute the requested operation
            if operation == "list_files":
                result = self._list_files(service, query, folder_id)
            elif operation == "upload_file":
                result = self._upload_file(service, file_path, folder_id, mime_type)
            elif operation == "download_file":
                result = self._download_file(service, file_id, file_path)
            elif operation == "create_folder":
                result = self._create_folder(service, name, folder_id)
            elif operation == "share_file":
                result = self._share_file(service, file_id, eval(permissions))
            elif operation == "list_folder_contents":
                result = self._list_files(service, folder_id=folder_id)
            else:
                raise ValueError(f"Unsupported operation: {operation}")

            # Store the result and set success outcome
            self.result = {
                "operation": operation,
                "timestamp": datetime.now().isoformat(),
                "data": result
            }
            self.outcome = "success"

        except ValueError as e:
            self.outcome = "apiError"
        except Exception as e:
            if not self.outcome:
                self.outcome = "apiError"

