import requests
from utils.logger import logger as log

BASE_URL = "https://api.chess.com/pub/player/{PLAYER_USERNAME}/"
GAMES_MONTHLY_URL = "games/{YYYY}/{MM}"


def download_games_chesscom(username, year, month, drive, folder_id, start_idx=0):
    log.info(f"Downloading games from Chess.com for {username} for {month}/{year}")
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
        log.error("Error in fetching the games from Chess.com")
        return None, False

    games_obj = response.json().get("games", None)
    if not games_obj:
        log.info("Chesscom: No games found!")
        return 0, False
    for idx, game in enumerate(games_obj):
        game_pgn = game.get("pgn", None)
        if not game_pgn:
            continue
        drive.upload_game_to_drive(
            file_name=start_idx + idx + 1,
            game=game_pgn,
            folder_id=folder_id,
        )
    total_games = len(games_obj)

    log.info(f"Downloaded {total_games} games from Chess.com for {username}")
    return total_games, True
