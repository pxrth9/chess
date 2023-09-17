import sys

from lichess import import_game_lichess
from cus_email import send_email
from chesscom import download_games_chesscom


def main(PLAYER_USERNAME, MONTH, YEAR):
    games, is_success, folder_path = download_games_chesscom(
        PLAYER_USERNAME, YEAR, MONTH
    )

    if not is_success:
        print("Error fetching the games")
        sys.exit(1)

    games_url = list()

    # Iterate over the games and download the PGN files
    for idx, game in enumerate(games):
        game_pgn = game.get("pgn", "")

        lichess_url, is_success = import_game_lichess(game_pgn)

        if not is_success:
            print("Error importing the game")
            # Save the PGN into a new file in the folder created above
            with open(f"{folder_path}/{idx}.pgn", "w") as f:
                f.write(game_pgn)
            continue
        else:
            games_url.append(lichess_url)

    print(f"{games - len(games_url)} games downloaded successfully")

    # Send the message to the user
    message = f"{len(games_url)} games downloaded successfully for {PLAYER_USERNAME} for {MONTH}/{YEAR}\n\n {games_url}"

    send_email("Chess Games", message)

    if not is_success:
        print("Error sending the message")
        sys.exit(1)
    print("Message sent successfully")
    return


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <username> <month> <year>")
        sys.exit(1)

    PLAYER_USERNAME, MONTH, YEAR = sys.argv[1:]
    main()
