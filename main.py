import sys
import os
import json
import logging
from email_user import send_email
from chesscom import download_games_chesscom
from lichess import download_games_lichess
from g_drive import upload_games
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
DEFAULT_CONCURRENT_USERS = 3

# Load environment variables
try:
    CHESS_USERS = json.loads(os.environ.get("CHESS_USERS", "[]"))
    if not isinstance(CHESS_USERS, list):
        raise ValueError("CHESS_USERS must be a JSON array.")
except Exception as e:
    logging.error(f"Invalid CHESS_USERS environment variable: {e}")
    sys.exit(1)

CONCURRENT_USERS = int(os.environ.get("CONCURRENT_USERS", DEFAULT_CONCURRENT_USERS))


def process_player(player, month, year):
    """Process a single player's games and upload them to Google Drive."""
    player_name = player.get("name", "Unknown").upper()
    chesscom_username = player.get("chesscom_username")
    lichess_username = player.get("lichess_username")

    logging.info(f"Processing player: {player_name}")

    # Download games from Chess.com
    chesscom_games, chesscom_is_success = [], False
    if chesscom_username:
        try:
            logging.info(f"Downloading games from Chess.com for {chesscom_username}")
            chesscom_games, chesscom_is_success = download_games_chesscom(
                username=chesscom_username, year=year, month=month
            )
        except Exception as e:
            logging.error(
                f"Error downloading games from Chess.com for {chesscom_username}: {e}"
            )

    # Download games from Lichess
    lichess_games, lichess_is_success = [], False
    if lichess_username:
        try:
            logging.info(f"Downloading games from Lichess for {lichess_username}")
            lichess_games, lichess_is_success = download_games_lichess(
                username=lichess_username, year=year, month=month
            )
        except Exception as e:
            logging.error(
                f"Error downloading games from Lichess for {lichess_username}: {e}"
            )

    # Combine games from both platforms
    games = chesscom_games + lichess_games

    # Upload games to Google Drive
    try:
        logging.info(f"Uploading games to Google Drive for {player_name}")
        upload_games(player_name, year, month, games)
    except Exception as e:
        logging.error(f"Error uploading games to Google Drive for {player_name}: {e}")

    # Log and return the status message
    logging.info(f"{len(games)} games downloaded successfully for {player_name}")
    message = (
        f"Player Name: {player_name}.\n"
        f"Job Status: Chess.com: {chesscom_is_success}, Lichess: {lichess_is_success}.\n"
        f"{len(games)} games downloaded successfully for {month}/{year}.\n"
    )
    return message


def main(month, year):
    """Main function to process all players and send an email with the results."""
    if not CHESS_USERS:
        logging.error("No users to fetch games for.")
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
            logging.error(f"Error processing players: {e}")
            sys.exit(1)

    # Send the email with all messages
    final_message = "\n".join(all_messages)
    try:
        is_success = send_email("GitHub Action -- Chess Games", final_message)
        if not is_success:
            logging.error("Error sending the email.")
            sys.exit(1)
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logging.error("Usage: python main.py <month> <year>")
        sys.exit(1)

    MONTH, YEAR = sys.argv[1], sys.argv[2]

    # Validate month and year
    if not MONTH.isdigit() or not YEAR.isdigit():
        logging.error("Month and year must be numeric.")
        sys.exit(1)

    main(MONTH, YEAR)