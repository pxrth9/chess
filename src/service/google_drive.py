import concurrent
import random
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import sys
import io
import json
from googleapiclient.http import MediaIoBaseUpload
from utils.logger import logger as log
from googleapiclient.errors import HttpError


from utils.b_64 import decode_token

# Constants
DEFAULT_FOLDER_NAME = "Chess"
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
PGN_MIME_TYPE = "application/x-chess-pgn"


def get_drive_service():
    try:
        scope = json.loads(
            os.environ.get("GCP_SCOPES", '["https://www.googleapis.com/auth/drive"]')
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


def get_folder_id(service, folder_name, parent_folder_id=None):
    query = f"mimeType = '{FOLDER_MIME_TYPE}' and name = '{folder_name}'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"
    try:
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
        return items[0]["id"] if items else None
    except Exception as e:
        log.error(f"Error retrieving folder ID for '{folder_name}': {e}")
        return None


def create_folder(service, folder_name, parent_folder_id=None):
    file_metadata = {
        "name": folder_name,
        "mimeType": FOLDER_MIME_TYPE,
        "parents": [parent_folder_id] if parent_folder_id else [],
    }
    try:
        file = (
            service.files()
            .create(body=file_metadata, fields="id, parents", supportsAllDrives=True)
            .execute()
        )
        return file.get("id")
    except Exception as e:
        log.error(f"Error creating folder '{folder_name}': {e}")
        sys.exit(1)


def get_or_create_folder(username, service, folder_name, parent_folder_id=None):
    folder_id = get_folder_id(service, folder_name, parent_folder_id)
    if not folder_id:
        log.info(
            f"Username: {username}. Folder '{folder_name}' not found, creating it."
        )
        folder_id = create_folder(service, folder_name, parent_folder_id)
    return folder_id


def upload_single_file(service, game, file_name, folder_id, max_attempts=5):
    attempt = 0
    delay = 1
    while attempt < max_attempts:
        try:
            with io.BytesIO(game.encode("utf-8")) as file_stream:
                file_metadata = {"name": file_name, "parents": [folder_id]}
                media = MediaIoBaseUpload(file_stream, mimetype=PGN_MIME_TYPE)
                response = (
                    service.files()
                    .create(
                        body=file_metadata,
                        media_body=media,
                        fields="id",
                        supportsAllDrives=True,
                    )
                    .execute()
                )
                return response
        except HttpError as e:
            # Only retry if we see certain status codes (e.g., rate limit and server errors)
            if e.resp.status in [403, 429, 500, 503]:
                attempt += 1
                log.warning(
                    f"Attempt {attempt} for {file_name} failed with HTTP status {e.resp.status}. "
                    f"Retrying in {delay} seconds..."
                )
                # Wait with a delay and a slight random jitter
                time.sleep(delay + random.uniform(0, 0.1))
                delay *= 2  # exponential backoff
            else:
                # For other HTTP errors, log and break without retrying
                log.error(f"Non-retryable HttpError uploading file '{file_name}': {e}")
                raise
        except Exception as e:
            # For non-HTTP errors, do not retry
            log.error(f"Error uploading file '{file_name}': {e}")
            raise

    log.error(f"Max attempts reached for {file_name}. Giving up.")
    return None


def upload_files_to_drive(username, service, games, folder_id, concurent_uploads):
    log.info(
        f"Username: {username}. Starting upload of {len(games)} files to folder ID: {folder_id}"
    )
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=concurent_uploads
    ) as executor:
        futures = []
        for idx, game in enumerate(games):
            file_name = f"{idx}.pgn"
            futures.append(
                executor.submit(upload_single_file, service, game, file_name, folder_id)
            )
        for future in concurrent.futures.as_completed(futures):
            result = future.result()  # This will raise any exception that occurred.

    log.info("All files have been processed.")


def upload_games(username, year, month, games, concurrent_uploads):
    service = get_drive_service()

    try:
        # Get or create the folder hierarchy
        default_folder_id = get_or_create_folder(username, service, DEFAULT_FOLDER_NAME)
        user_folder_id = get_or_create_folder(
            username, service, username, default_folder_id
        )
        year_folder_id = get_or_create_folder(username, service, year, user_folder_id)
        month_folder_id = get_or_create_folder(username, service, month, year_folder_id)

        # Upload the games
        upload_files_to_drive(
            username, service, games, month_folder_id, concurrent_uploads
        )
    except Exception as e:
        log.error(f"Error during game upload process: {e}")
        sys.exit(1)
