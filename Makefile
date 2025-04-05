.PHONY: init run


init:
	@ echo "Initializing project..."
	@ pip install -r requirements.txt
	@ echo "Project initialized."

run:
	@ echo "Running project..."
	@ set -a && . .env && python3 src/main.py 03 2025
	@ echo "Project finished."