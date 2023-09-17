import requests
import os

BASE_URL = "https://lichess.org"
IMPORT_ENDPOINT = "/api/import"

# LICHESS_API_TOKEN = os.environ.get("lichess_token")
LICHESS_API_TOKEN = "lip_FWnCSwhybQEeKApy2TNB"


def import_game_lichess(
    pgn: str,
    token=LICHESS_API_TOKEN,
):
    if not token:
        print("No token found")
        return None, False

    request_url = BASE_URL + IMPORT_ENDPOINT
    response = requests.post(
        request_url,
        data={
            "pgn": pgn,
        },
        headers={
            "Content-type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {token}",
        },
    )
    if response.status_code != 200:
        print(response.status_code)
        print("Error Importing the game")
        return None, False

    url = response.json().get("url", None)
    if not url:
        print("Error Getting the URL")
        return None, False
    return url, True
