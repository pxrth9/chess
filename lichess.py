import berserk
import os

LICHESS_TOKEN = os.environ.get("LICHESS_TOKEN")


def download_games_lichess(username, since, until):
    session = berserk.TokenSession(LICHESS_TOKEN)
    client = berserk.Client(session=session)
    start, end = berserk.utils.to_millis(since), berserk.utils.to_millis(until)
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
