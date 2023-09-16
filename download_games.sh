#!/bin/bash

BASE_URL="https://api.chess.com/pub/player/"
GAMES="/games/"
MONTH=$1
echo "$MONTH"
MONTH=$(printf "%02d" "$1")
echo "$MONTH"
YEAR=$2
echo "$YEAR"
echo "$0 $1 $2"
PLAYER_USERNAME="pparth86"

# Create the Games folder if it doesn't exist
mkdir -p "Games/$YEAR/$MONTH"

REQUEST_URL="$BASE_URL$PLAYER_USERNAME$GAMES$YEAR/$MONTH"
echo "$REQUEST_URL"
RESPONSE=$(curl -s "$REQUEST_URL")
echo "$RESPONSE"

# get the length of the games array
GAMES_LENGTH=$(echo "$RESPONSE" | jq '.games | length')
echo "Number of Games: $GAMES_LENGTH "

# Loop through all games in the response
for ((i = 0; i < GAMES_LENGTH; i++)); do
    PGN=$(echo "$RESPONSE" | jq -r ".games[$i].pgn")
    echo "$PGN" > "Games/$YEAR/$MONTH/$i.pgn"
done

echo "Done!"
