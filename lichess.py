import berserk
import os
import datetime

LICHESS_TOKEN = os.environ.get("LICHESS_TOKEN")  # or "lip_hSqWwFvF3JQSNDlHlWcU"


def download_games_lichess(username, since, until):
    session = berserk.TokenSession(LICHESS_TOKEN)
    client = berserk.Client(session=session)

    start, end = berserk.utils.to_millis(
        datetime.datetime(2025, 1, 1)
    ), berserk.utils.to_millis(datetime.datetime(2025, 1, 30))

    games_resp = client.games.export_by_player(
        username=username,
        since=start,
        until=end,
        as_pgn=True,
    )
    games = list(games_resp)
    if not games:
        print("No games found in Lichess")
        return None, False

    return games, True
