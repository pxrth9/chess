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

CHESS_USERS = json.loads(os.environ.get("CHESS_USERS") or "[]")
CONCURENT_USERS = int(os.environ.get("CONCURENT_USERS") or 3)


def main(player, month, year):
    player_name = player["name"].upper()
    chesscom_username = (
        player["chesscom_username"] if "chesscom_username" in player else None
    )
    lichess_username = (
        player["lichess_username"] if "lichess_username" in player else None
    )

    logging.info(f"Processing player: {player_name}")

    # Download the games from Chess.com
    if chesscom_username:
        logging.info(f"Downloading games from Chess.com for {chesscom_username}")
        chesscom_games, chesscom_is_success = download_games_chesscom(
            username=chesscom_username, year=year, month=month
        )
    else:
        chesscom_games = []
        chesscom_is_success = False

    # Download the games from Lichess
    if lichess_username:
        logging.info(f"Downloading games from Lichess for {lichess_username}")
        lichess_games, lichess_is_success = download_games_lichess(
            username=lichess_username,
            year=year,
            month=month,
        )
    else:
        lichess_games = []
        lichess_is_success = False

    games = []
    if chesscom_is_success:
        games.extend(chesscom_games)
    if lichess_is_success:
        games.extend(lichess_games)

    # Upload the games to the Google Drive
    logging.info(f"Uploading games to Google Drive for {player_name}")
    upload_games(player_name, year, month, games)

    logging.info(f"{len(games)} games downloaded successfully")

    # Return the status and message for the player
    message = f"Player Name: {player_name}.\n"
    message += f"Job Status: Chess.com: {chesscom_is_success}, Lichess: {lichess_is_success}.\n"
    message += f"{len(games)} games downloaded successfully for {month}/{year}.\n"

    return message


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logging.error("Usage: python script.py <month> <year>")
        sys.exit(1)

    if not CHESS_USERS:
        logging.error("No users to fetch games for")
        sys.exit(1)

    MONTH, YEAR = sys.argv[1:]

    all_messages = []
    def process_player(player):
        return main(player, MONTH, YEAR)

    with ThreadPoolExecutor(max_workers=CONCURENT_USERS) as executor:
        results = executor.map(process_player, CHESS_USERS)
        all_messages.extend(results)

    # Send the email with all messages
    final_message = "\n".join(all_messages)
    is_success = send_email("GitHub Action -- Chess Games", final_message)

    if not is_success:
        logging.error("Error sending the message")
        sys.exit(1)
    logging.info("Message sent successfully")
