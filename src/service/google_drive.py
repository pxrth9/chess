from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import sys
import io
import json
from googleapiclient.http import MediaIoBaseUpload
from utils.logger import logger as log

from utils.b_64 import decode_token


class GoogleDrive:
    # Constants
    DEFAULT_FOLDER_NAME = "Chess"
    FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"

    def __init__(self):
        self.svc = self.get_drive_service()

    def get_drive_service(self):
        try:
            scope = json.loads(
                os.environ.get(
                    "GCP_SCOPES", '["https://www.googleapis.com/auth/drive"]'
                )
            )
            if not isinstance(scope, list):
                raise ValueError("GCP_SCOPES must be a JSON array of strings.")

            gcp_credentials = os.environ.get("GCP_CREDENTIALS")
            if not gcp_credentials:
                raise ValueError("GCP_CREDENTIALS environment variable is not set.")

            json_info = json.loads(decode_token(gcp_credentials))
            credentials = service_account.Credentials.from_service_account_info(
                info=json_info, scopes=scope
            )
            return build("drive", "v3", credentials=credentials, cache_discovery=False)
        except Exception as e:
            log.error(f"Failed to initialize Google Drive service: {e}")
            sys.exit(1)

    def get_folder_id(self, folder_name, parent_folder_id=None):
        query = (
            f"mimeType = '{GoogleDrive.FOLDER_MIME_TYPE}' and name = '{folder_name}'"
        )
        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"
        try:
            results = (
                self.svc.files()
                .list(
                    fields="files(id, name, mimeType)",
                    q=query,
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                )
                .execute()
            )
            items = results.get("files", [])
            return items[0]["id"] if items else None
        except Exception as e:
            log.error(f"Error retrieving folder ID for '{folder_name}': {e}")
            return None

    def create_folder(self, folder_name, parent_folder_id=None):
        file_metadata = {
            "name": folder_name,
            "mimeType": GoogleDrive.FOLDER_MIME_TYPE,
            "parents": [parent_folder_id] if parent_folder_id else [],
        }
        folder_id = None
        try:
            file = (
                self.svc.files()
                .create(
                    body=file_metadata, fields="id, parents", supportsAllDrives=True
                )
                .execute()
            )
            return file.get("id")
        except Exception as e:
            log.error(f"Error creating folder '{folder_name}': {e}")
            sys.exit(1)

    def get_or_create_folder(self, username, folder_name, parent_folder_id=None):
        folder_id = self.get_folder_id(folder_name, parent_folder_id)
        if not folder_id:
            log.info(
                f"Username: {username}. Folder '{folder_name}' not found, creating it."
            )
            folder_id = self.create_folder(folder_name, parent_folder_id)
        return folder_id

    def upload_game_to_drive(self, file_name, game, folder_id):
        file_name = f"{file_name}.pgn"
        try:
            # Use context manager for file stream
            with io.BytesIO(game.encode("utf-8")) as file_stream:
                file_metadata = {"name": file_name, "parents": [folder_id]}
                media = MediaIoBaseUpload(
                    file_stream, mimetype="application/x-chess-pgn"
                )
                self.svc.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields="id",
                    supportsAllDrives=True,
                ).execute()
        except Exception as e:
            log.error(f"Error uploading file '{file_name}': {e}")

    def create_folders(self, username, year, month):
        try:
            # Get or create the folder hierarchy
            default_folder_id = self.get_folder_id(GoogleDrive.DEFAULT_FOLDER_NAME)
            if not default_folder_id:
                log.info(
                    f"Username: {username}. Default folder '{GoogleDrive.DEFAULT_FOLDER_NAME}' not found"
                )
                return None
            user_folder_id = self.get_or_create_folder(
                username, username, default_folder_id
            )
            year_folder_id = self.get_or_create_folder(username, year, user_folder_id)
            month_folder_id = self.get_or_create_folder(username, month, year_folder_id)

            return month_folder_id
        except Exception as e:
            log.error(f"Error during game upload process: {e}")
            sys.exit(1)
