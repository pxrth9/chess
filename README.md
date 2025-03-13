# Get Started with this project

```bash

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


export CHESS_USERS='[{"name": "PARTH","chesscom_username":"pparth86","lichess_username":"pxrth9"}]'
export LICHESS_TOKEN=$(cat .token_lichess.b64)
export GCP_CREDENTIALS=$(cat .token_gcp.b64)

# Run the app
python3 main.py <month> <year>
# Deactivate venv
deactivate
```
