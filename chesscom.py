import os
import requests

BASE_URL = "https://api.chess.com/pub/player/{PLAYER_USERNAME}/"
GAMES_MONTHLY_URL = "games/{YYYY}/{MM}"


def create_game_folder(username, year, month):
    folder_path = f"Games/{username}/{year}/{month}"
    os.makedirs(
        folder_path, exist_ok=True
    )  # Use exist_ok to avoid errors if the folder already exists
    return folder_path


def download_games_chesscom(username, year, month):
    # Create the folder for the games
    folder_path = create_game_folder(username, year, month)

    # Construct the URL
    request_url = BASE_URL.format(PLAYER_USERNAME=username) + GAMES_MONTHLY_URL.format(
        YYYY=year, MM=month
    )

    # Make the GET request
    response = requests.get(
        request_url,
        headers={"Content-type": "application/json", "User-Agent": "Mozilla/5.0"},
    )

    if response.status_code not in [200, 204]:
        print("Error in fetching the games")
        return None, False, folder_path

    games = response.json().get("games", None)

    if not games:
        print("No games found")
        return None, False, folder_path

    return games, True, folder_path
