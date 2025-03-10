import sys
import os
from cus_email import send_email
from chesscom import download_games_chesscom
from lichess import download_games_lichess
from datetime import datetime, timedelta


USERS = {"PARTH": {"CHESS_USERNAME": "pparth86", "LICHESS_USERNAME": "pxrth9"}}


def create_game_folder(username, year, month):
    folder_path = f"Games/{username}/{year}/{month}"
    os.makedirs(
        folder_path, exist_ok=True
    )  # Use exist_ok to avoid errors if the folder already exists
    return folder_path


def get_previous_month_timestamps():
    today = datetime.today()
    last_day_previous_month = today.replace(day=1) - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)
    return first_day_previous_month, last_day_previous_month


def main(player_name):

    first_day_previous_month, last_day_previous_month = get_previous_month_timestamps()
    year = first_day_previous_month.strftime("%Y")
    month = first_day_previous_month.strftime("%m")

    # Create the folder for the games
    folder_path = create_game_folder(
        player_name,
        year=year,
        month=month,
    )

    games = list()
    chesscom_games, chesscom_is_success = ["1"], False
    chesscom_games, chesscom_is_success = download_games_chesscom(
        username=USERS["PARTH"]["CHESS_USERNAME"], year=year, month=month
    )

    liches_games, lichess_is_success = download_games_lichess(
        username=USERS["PARTH"]["LICHESS_USERNAME"],
        since=first_day_previous_month,
        until=last_day_previous_month,
    )

    if chesscom_is_success:
        games.extend(chesscom_games)
    else:
        print("Error fetching the games from Chess.com")
    if lichess_is_success:
        games.extend(liches_games)
    else:
        print("Error fetching the games from Lichess")

    # Iterate over the games and download the PGN files
    for idx, game in enumerate(games):
        # Save the PGN into a new file in the folder created above
        with open(f"{folder_path}/{idx}.pgn", "w") as f:
            f.write(game)

    print(f"{len(games)} games downloaded successfully")

    # Send the message to the user
    status = f"Chess.com: {chesscom_is_success}, Lichess: {lichess_is_success}"
    message = f"Job Staus: {status}.\n{len(games)} games downloaded successfully for {player_name} for {month}/{year}"

    is_success = send_email("GitHub Action -- Chess Games", message)

    if not is_success:
        print("Error sending the message")
        sys.exit(1)
    print("Message sent successfully")
    return


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <username>")
        sys.exit(1)

    PLAYER_USERNAME = sys.argv[1]
    main(PLAYER_USERNAME)
