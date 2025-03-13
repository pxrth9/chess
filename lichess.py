import berserk
import os
from datetime import datetime
import calendar


LICHESS_TOKEN = os.environ.get("LICHESS_TOKEN") or ""

from b_64 import decode_token


def get_month_start_end_timestamps(year, month):
    # Convert string inputs to integers
    year = int(year)
    month = int(month)

    # Start date: First day of the month at midnight
    start_date = datetime(year, month, 1)

    # End date: Last day of the month at 23:59:59
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, last_day, 23, 59, 59)

    # Convert to Unix timestamps
    start = berserk.utils.to_millis(start_date)
    end = berserk.utils.to_millis(end_date)

    return start, end


def download_games_lichess(username, year, month):
    token = decode_token(LICHESS_TOKEN)
    session = berserk.TokenSession(token)
    client = berserk.Client(session=session)
    start, end = get_month_start_end_timestamps(year, month)
    games_resp = client.games.export_by_player(
        username=username,
        since=start,
        until=end,
        as_pgn=True,
    )
    games = list(games_resp)
    if not games:
        print("Lichess: No games found!")
        return None, False

    return games, True
