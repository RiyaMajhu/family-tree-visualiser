import pandas as pd
import psycopg
from db_config import DB_SETTINGS
from clean_data import load_clean_data


def to_rows(df):
    # turn a table into a list of rows the database understands
    # (blanks become None, numbers become normal Python numbers)
    rows = []
    for row in df.itertuples(index=False, name=None):
        rows.append(tuple(
            None if pd.isna(v) else (v.item() if hasattr(v, "item") else v)
            for v in row
        ))
    return rows


people, families, children = load_clean_data()

with psycopg.connect(**DB_SETTINGS) as conn:
    with conn.cursor() as cur:
        # empty the tables first so this can be re-run safely
        cur.execute("TRUNCATE family_children, families, people")

        cur.executemany(
            "INSERT INTO people (id, forenames, surname, birth, death) VALUES (%s, %s, %s, %s, %s)",
            to_rows(people[["Id", "Forenames", "Surname", "Birth", "Death"]]),
        )
        cur.executemany(
            "INSERT INTO families (id, father_id, mother_id) VALUES (%s, %s, %s)",
            to_rows(families),
        )
        cur.executemany(
            "INSERT INTO family_children (family_id, child_id) VALUES (%s, %s)",
            to_rows(children),
        )

    print("Imported", len(people), "people,", len(families), "families and", len(children), "parent-child links")