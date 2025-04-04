import requests
from utils.logger import logger as log

BASE_URL = "https://api.chess.com/pub/player/{PLAYER_USERNAME}/"
GAMES_MONTHLY_URL = "games/{YYYY}/{MM}"


def download_games_chesscom(username, year, month):
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

    games = list()
    games_obj = response.json().get("games", None)
    for game in games_obj:
        game_pgn = game.get("pgn", None)
        if not game_pgn:
            continue
        games.append(game_pgn)
    if not games:
        log.info("Chesscom: No games found!")
        return None, False

    log.info(f"Downloaded {len(games)} games from Chess.com for {username}")
    return games, True
