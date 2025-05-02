import sys
import os
import json
from utils.email_user import send_email
from service.chess_com import download_games_chesscom
from service.lichess import download_games_lichess
from service.google_drive import GoogleDrive
from concurrent.futures import ThreadPoolExecutor
from utils.logger import logger as log

# Constants
DEFAULT_CONCURRENT_USERS = 3

# Load environment variables
try:
    CHESS_USERS = json.loads(os.environ.get("CHESS_USERS", "[]"))
    if not isinstance(CHESS_USERS, list):
        raise ValueError("CHESS_USERS must be a JSON array.")
except Exception as e:
    log.error(f"Invalid CHESS_USERS environment variable: {e}")
    sys.exit(1)

CONCURRENT_USERS = int(os.environ.get("CONCURRENT_USERS", DEFAULT_CONCURRENT_USERS))


def process_player(player, month, year):
    """Process a single player's games and upload them to Google Drive."""
    player_name = player.get("name", "Unknown").upper()
    chesscom_username = player.get("chesscom_username")
    lichess_username = player.get("lichess_username")
    player_email = player.get("email")

    log.info(f"Processing player: {player_name}")

    # Create Google Drive Folder
    drive = GoogleDrive()
    month_folder_id = drive.create_folders(
        username=player_name,
        year=year,
        month=month,
    )

    # Download games from Chess.com
    num_chesscom_games, chesscom_is_success = 0, False
    if chesscom_username:
        try:
            num_chesscom_games, chesscom_is_success = download_games_chesscom(
                username=chesscom_username,
                year=year,
                month=month,
                drive=drive,
                folder_id=month_folder_id,
            )
        except Exception as e:
            log.error(
                f"Error downloading games from Chess.com for {chesscom_username}: {e}"
            )

    # Download games from Lichess
    num_lichess_games, lichess_is_success = 0, False
    if lichess_username:
        try:
            num_lichess_games, curr_count, lichess_is_success = download_games_lichess(
                username=lichess_username,
                year=year,
                month=month,
                drive=drive,
                folder_id=month_folder_id,
                start_idx=num_chesscom_games,
            )
        except Exception as e:
            log.error(
                f"Error downloading games from Lichess for {lichess_username}: {e}"
            )

    message = f"Player Name: {player_name}.\n"
    if num_chesscom_games > 0:
        message += f"Chess.com: {chesscom_is_success}, Games Downloaded: {num_chesscom_games}\n"

    if num_lichess_games > 0:
        message += (
            f"Lichess: {lichess_is_success}, Games Downloaded: {num_lichess_games}.\n"
        )

    message += f"{curr_count} total games downloaded successfully for {player}/{month}/{year}.\n"

    return message


def main(month, year):
    """Main function to process all players and send an email with the results."""
    if not CHESS_USERS:
        log.error("No users to fetch games for.")
        sys.exit(1)

    all_messages = []

    # Process players concurrently
    with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        try:
            results = executor.map(
                lambda player: process_player(player, month, year), CHESS_USERS
            )
            all_messages.extend(results)
        except Exception as e:
            log.error(f"Error processing players: {e}")
            sys.exit(1)

    # Send the email with all messages
    final_message = "\n".join(all_messages)
    try:
        send_email("GitHub Action -- Chess Games", final_message)
    except Exception as e:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        log.error("Usage: python main.py <month> <year>")
        sys.exit(1)

    MONTH, YEAR = sys.argv[1], sys.argv[2]

    # Validate month and year
    if not MONTH.isdigit() or not YEAR.isdigit():
        log.error("Month and year must be numeric.")
        sys.exit(1)

    main(MONTH, YEAR)
