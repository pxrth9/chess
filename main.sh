#!/bin/bash

BASE_URL="https://api.chess.com/pub/player/"
GAMES="/games/"
YEAR="2023"
MONTHS=( "07" "08" "09")
PLAYER_USERNAME="pparth86"

# Create the Games folder if it doesn't exist
mkdir -p Games

for month in "${MONTHS[@]}"; do
    VAR=1
    mkdir -p "Games/$month"
    REQUEST_URL="$BASE_URL$PLAYER_USERNAME$GAMES$YEAR/$month"
    RESPONSE=$(curl -s "$REQUEST_URL")

    # get the length of the games array
    GAMES_LENGTH=$(echo "$RESPONSE" | jq '.games | length')
    
    echo "Month: $month"
    echo "Number of Games: $GAMES_LENGTH "

    # Loop through all games in the response
    for ((i = 0; i < GAMES_LENGTH; i++)); do
        PGN=$(echo "$RESPONSE" | jq -r ".games[$i].pgn")
        echo "$PGN" > "Games/$month/$VAR.pgn"
        VAR=$((VAR+1))
    done
done

echo "Done!"
