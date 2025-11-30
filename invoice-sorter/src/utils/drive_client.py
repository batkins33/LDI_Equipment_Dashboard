"""Google Drive API client"""

import os
import io
from typing import List, Optional, Dict, Any
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class DriveClient:
    """Client for interacting with Google Drive API"""

    def __init__(self, credentials_path: Optional[str] = None):
        """Initialize Drive client

        Args:
            credentials_path: Path to service account credentials JSON
        """
        self.credentials_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.service = self._get_service()

    def _get_service(self):
        """Get Drive API service instance"""
        if self.credentials_path and os.path.exists(self.credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            return build('drive', 'v3', credentials=credentials)
        else:
            # For development/testing without credentials
            print("Warning: No credentials found. Drive operations will fail.")
            return None

    def list_files(
        self,
        folder_id: str,
        mime_type: Optional[str] = None,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """List files in a folder

        Args:
            folder_id: Google Drive folder ID
            mime_type: Filter by MIME type (e.g., 'application/pdf')
            page_size: Number of results per page

        Returns:
            List of file metadata dictionaries
        """
        if not self.service:
            return []

        try:
            query = f"'{folder_id}' in parents and trashed=false"
            if mime_type:
                query += f" and mimeType='{mime_type}'"

            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime)"
            ).execute()

            return results.get('files', [])

        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def download_file(self, file_id: str, destination_path: str) -> bool:
        """Download file from Google Drive

        Args:
            file_id: Google Drive file ID
            destination_path: Local path to save file

        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False

        try:
            request = self.service.files().get_media(fileId=file_id)

            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

            with io.FileIO(destination_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"Download {int(status.progress() * 100)}%")

            return True

        except Exception as e:
            print(f"Error downloading file: {e}")
            return False

    def upload_file(
        self,
        file_path: str,
        folder_id: str,
        new_name: Optional[str] = None
    ) -> Optional[str]:
        """Upload file to Google Drive

        Args:
            file_path: Local file path
            folder_id: Destination folder ID
            new_name: New name for the file (optional)

        Returns:
            File ID if successful, None otherwise
        """
        if not self.service:
            return None

        try:
            file_name = new_name or os.path.basename(file_path)

            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }

            media = MediaFileUpload(file_path, resumable=True)

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            return file.get('id')

        except Exception as e:
            print(f"Error uploading file: {e}")
            return None

    def move_file(
        self,
        file_id: str,
        destination_folder_id: str,
        new_name: Optional[str] = None
    ) -> bool:
        """Move file to another folder

        Args:
            file_id: File ID to move
            destination_folder_id: Destination folder ID
            new_name: New name for the file (optional)

        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False

        try:
            # Get current parents
            file = self.service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()

            previous_parents = ",".join(file.get('parents', []))

            # Build update metadata
            update_metadata = {}
            if new_name:
                update_metadata['name'] = new_name

            # Move file
            self.service.files().update(
                fileId=file_id,
                addParents=destination_folder_id,
                removeParents=previous_parents,
                body=update_metadata,
                fields='id, parents'
            ).execute()

            return True

        except Exception as e:
            print(f"Error moving file: {e}")
            return False

    def copy_file(
        self,
        file_id: str,
        destination_folder_id: str,
        new_name: Optional[str] = None
    ) -> Optional[str]:
        """Copy file to another folder

        Args:
            file_id: File ID to copy
            destination_folder_id: Destination folder ID
            new_name: New name for the file (optional)

        Returns:
            New file ID if successful, None otherwise
        """
        if not self.service:
            return None

        try:
            file_metadata = {
                'parents': [destination_folder_id]
            }
            if new_name:
                file_metadata['name'] = new_name

            file = self.service.files().copy(
                fileId=file_id,
                body=file_metadata,
                fields='id'
            ).execute()

            return file.get('id')

        except Exception as e:
            print(f"Error copying file: {e}")
            return None

    def delete_file(self, file_id: str) -> bool:
        """Delete file from Google Drive

        Args:
            file_id: File ID to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False

        try:
            self.service.files().delete(fileId=file_id).execute()
            return True

        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file metadata

        Args:
            file_id: File ID

        Returns:
            File metadata dictionary
        """
        if not self.service:
            return None

        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, createdTime, modifiedTime, size'
            ).execute()
            return file

        except Exception as e:
            print(f"Error getting file metadata: {e}")
            return None

    def create_folder(self, name: str, parent_folder_id: Optional[str] = None) -> Optional[str]:
        """Create a new folder

        Args:
            name: Folder name
            parent_folder_id: Parent folder ID (optional)

        Returns:
            Folder ID if successful, None otherwise
        """
        if not self.service:
            return None

        try:
            file_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]

            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            return folder.get('id')

        except Exception as e:
            print(f"Error creating folder: {e}")
            return None
