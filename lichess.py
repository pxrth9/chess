import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://lichess.org"
IMPORT_ENDPOINT = "/api/import"

LICHESS_API_TOKEN = os.environ.get("LICHESS_API_TOKEN")

# Create a session with built-in retry mechanisms
session = requests.Session()

# Define retry settings


adapter = HTTPAdapter(
    max_retries=Retry(
        total=3,  # Maximum number of retries (adjust as needed)
        backoff_factor=1,  # Exponential backoff factor (1 means linear backoff)
        status_forcelist=[429],  # Retry only on 429 (Too Many Requests) response
    )
)
session.mount(BASE_URL, adapter)

session.headers.update(
    {
        "Content-type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {LICHESS_API_TOKEN}",
    }
)


def import_game_lichess(pgn: str):
    if not LICHESS_API_TOKEN:
        print("No token found")
        return None, False

    request_url = BASE_URL + IMPORT_ENDPOINT

    try:
        response = session.post(
            request_url,
            data={
                "pgn": pgn,
            },
        )

        if response.status_code == 200:
            url = response.json().get("url", None)
            if not url:
                print("Error Getting the URL")
                return None, False
            return url, True
        else:
            print(response.status_code)
            print("Error Importing the game")
            return None, False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, False
