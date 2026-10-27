import psycopg
from db_config import DB_SETTINGS

with psycopg.connect(**DB_SETTINGS) as conn:
    with conn.cursor() as cur:
        # start fresh each time this runs
        cur.execute("DROP TABLE IF EXISTS family_children, families, people")

        cur.execute("""
            CREATE TABLE people (
                id        TEXT PRIMARY KEY,
                forenames TEXT,
                surname   TEXT,
                birth     INTEGER,
                death     INTEGER
            )
        """)

        cur.execute("""
            CREATE TABLE families (
                id        TEXT PRIMARY KEY,
                father_id TEXT REFERENCES people(id),
                mother_id TEXT REFERENCES people(id)
            )
        """)

        cur.execute("""
            CREATE TABLE family_children (
                family_id TEXT REFERENCES families(id),
                child_id  TEXT REFERENCES people(id),
                PRIMARY KEY (family_id, child_id)
            )
        """)

    print("Tables created!")