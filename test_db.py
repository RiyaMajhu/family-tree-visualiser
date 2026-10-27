import psycopg
from db_config import DB_SETTINGS

with psycopg.connect(**DB_SETTINGS) as conn:
    print("Connected to the database!")