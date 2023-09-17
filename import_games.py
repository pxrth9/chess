import requests
import json


BASE_URL = "https://lichess.org"
IMPORT_ENDPOINT = "/api/import"
LICHESS_API_TOKEN = os.environ.get('LICHESS_API_TOKEN')


def import_game_lichess(pgn :str, token=LICHESS_API_TOKEN,):
    request_url = BASE_URL+IMPORT_ENDPOINT
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {token}"
    }

    reponse = requests.post(request_url, data=pgn, headers=headers)
    if response.status_code != 200:
        print("Error Importing the game")
        return None, False
    
    url = reponse.json().get('url', None)
    if not url:
        return None, False

    return url, True
