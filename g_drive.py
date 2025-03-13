from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import sys
import io
import json
import logging
from googleapiclient.http import MediaIoBaseUpload

from b_64 import decode_token

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GCP_CREDENTIALS = os.environ.get("GCP_CREDENTIALS") or "e30K"  # {} is Default Value

DEFUALT_FOLDER_NAME = "Chess"
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"


def get_drive_service():
    scope = ["https://www.googleapis.com/auth/drive"]
    json_info = json.loads(decode_token(GCP_CREDENTIALS))
    credentials = service_account.Credentials.from_service_account_info(
        info=json_info, scopes=scope
    )
    return build("drive", "v3", credentials=credentials)


def get_folder_id(service, folder_name, parent_folder_id=None):
    query = f"mimeType = '{FOLDER_MIME_TYPE}' and name = '{folder_name}'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"
    results = (
        service.files()
        .list(
            fields="files(id, name, mimeType)",
            q=query,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
        )
        .execute()
    )
    items = results.get("files", [])
    if items:
        return items[0]["id"]
    return None


def create_folder(service, folder_name, parent_folder_id=None):
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id] if parent_folder_id else [],
    }
    file = (
        service.files()
        .create(body=file_metadata, fields="id, parents", supportsAllDrives=True)
        .execute()
    )

    return file.get("id")


def upload_files_to_drive(service, games, folder_id):
    logging.info(f"Uploading to folder-id: {folder_id}")
    for idx, game in enumerate(games):
        file_name = f"{idx}.pgn"

        # Create an in-memory file using BytesIO
        file_stream = io.BytesIO(game.encode("utf-8"))

        # Prepare file metadata and media upload
        file_metadata = {"name": file_name, "parents": [folder_id]}
        media = MediaIoBaseUpload(file_stream, mimetype="application/x-chess-pgn")

        # Upload the file
        _ = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id",
                supportsAllDrives=True,
            )
            .execute()
        )

        # Close the in-memory file
        file_stream.close()


def upload_games(username, year, month, games):
    # Get the service
    service = get_drive_service()

    # Get DEFUALT_FOLDER_NAME folder id
    default_folder_id = get_folder_id(service, DEFUALT_FOLDER_NAME)
    if not default_folder_id:
        logging.error(f"Folder {DEFUALT_FOLDER_NAME} not found. Exiting!")
        sys.exit(1)
    logging.info(f"Default Folder-id: {default_folder_id}")

    # Get User folder id
    user_folder_id = get_folder_id(
        service, username, parent_folder_id=default_folder_id
    )
    if not user_folder_id:
        logging.info(f"Folder {username} not found, creating it")
        user_folder_id = create_folder(
            service, username, parent_folder_id=default_folder_id
        )
    logging.info(f"User Folder-id: {user_folder_id}")

    # Get Year folder id
    year_folder_id = get_folder_id(service, year, parent_folder_id=user_folder_id)
    if not year_folder_id:
        logging.info(f"Folder {year} not found, creating it")
        year_folder_id = create_folder(service, year, parent_folder_id=user_folder_id)
    logging.info(f"Year Folder-id: {year_folder_id}")

    # Get Month folder id
    month_folder_id = get_folder_id(service, month, parent_folder_id=year_folder_id)
    if not month_folder_id:
        logging.info(f"Folder {month} not found, creating it")
        month_folder_id = create_folder(service, month, parent_folder_id=year_folder_id)
        logging.info(f"Folder-id: {month_folder_id}")
    logging.info(f"Month Folder-id: {month_folder_id}")

    # Upload the games
    upload_files_to_drive(service, games, month_folder_id)
