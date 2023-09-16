import os
import requests
import sys

BASE_URL = "https://api.chess.com/pub/player/{PLAYER_USERNAME}/"
GAMES_MONTHLY_URL = "games/{YYYY}/{MM}"


def create_game_folder(username, year, month):
    folder_path = f"Games/{year}/{month}/{username}"
    os.makedirs(
        folder_path, exist_ok=True
    )  # Use exist_ok to avoid errors if the folder already exists
    return folder_path


def fetch_and_save_games(username, year, month):
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
        return

    games = response.json().get("games", [])

    print(f"Total Games Found: {len(games)}")

    # Iterate over the games and download the PGN files
    for idx, game in enumerate(games):
        game_pgn = game.get("pgn", "")

        # Save the PGN into a new file in the folder created above
        with open(f"{folder_path}/{idx}.pgn", "w") as f:
            f.write(game_pgn)

    print("All games downloaded successfully")

    return len(games)


def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <username> <month> <year>")
        return

    PLAYER_USERNAME, MONTH, YEAR = sys.argv[1], sys.argv[2], sys.argv[3]
    total_games = fetch_and_save_games(PLAYER_USERNAME, YEAR, MONTH)
    sys.exit(total_games)


if __name__ == "__main__":
    total_games = main()
