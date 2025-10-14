- Create Database

CREATE DATABASE music_voting_db;

- In the /backend directory with venv activated
export FLASK_APP=run.py  # On Windows: set FLASK_APP=run.py

flask db init    # Run this only the first time
flask db migrate -m "Initial migration."
flask db upgrade