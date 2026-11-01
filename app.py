import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify, render_template
from db_config import DB_SETTINGS

app = Flask(__name__)


def get_connection():
    # dict_row means each row comes back like {"id": ..., "forenames": ...}
    return psycopg.connect(**DB_SETTINGS, row_factory=dict_row)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/person/<person_id>")
def person(person_id):
    with get_connection() as conn:
        cur = conn.cursor()

        # the person themselves
        cur.execute("SELECT * FROM people WHERE id = %s", (person_id,))
        me = cur.fetchone()
        if me is None:
            return jsonify({"error": "Person not found"}), 404

        # the family they were born into, and their parents
        cur.execute("""
            SELECT f.id, f.father_id, f.mother_id
            FROM family_children fc
            JOIN families f ON f.id = fc.family_id
            WHERE fc.child_id = %s
        """, (person_id,))
        birth_family = cur.fetchone()

        parents = []
        siblings = []
        if birth_family:
            cur.execute(
                "SELECT * FROM people WHERE id IN (%s, %s)",
                (birth_family["father_id"], birth_family["mother_id"]),
            )
            parents = cur.fetchall()

            cur.execute("""
                SELECT p.* FROM family_children fc
                JOIN people p ON p.id = fc.child_id
                WHERE fc.family_id = %s AND p.id <> %s
                ORDER BY p.birth
            """, (birth_family["id"], person_id))
            siblings = cur.fetchall()

        # every family where this person is a parent (one per partner)
        cur.execute(
            "SELECT * FROM families WHERE father_id = %s OR mother_id = %s",
            (person_id, person_id),
        )
        partnerships = []
        for fam in cur.fetchall():
            if fam["father_id"] == person_id:
                partner_id = fam["mother_id"]
            else:
                partner_id = fam["father_id"]

            partner = None
            if partner_id:
                cur.execute("SELECT * FROM people WHERE id = %s", (partner_id,))
                partner = cur.fetchone()

            cur.execute("""
                SELECT p.* FROM family_children fc
                JOIN people p ON p.id = fc.child_id
                WHERE fc.family_id = %s
                ORDER BY p.birth
            """, (fam["id"],))
            children = cur.fetchall()

            partnerships.append({"family": fam["id"], "partner": partner, "children": children})

    return jsonify({
        "person": me,
        "parents": parents,
        "siblings": siblings,
        "partnerships": partnerships,
    })


def years_text(birth, death):
    # e.g. "1848 - 1927", or "1930 - " if there's no death year
    birth_text = "?" if birth is None else str(birth)
    death_text = "" if death is None else str(death)
    return birth_text + " - " + death_text


@app.route("/api/tree")
def tree_data():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM people")
        people = cur.fetchall()
        cur.execute("SELECT * FROM families")
        families = cur.fetchall()
        cur.execute("SELECT * FROM family_children")
        links = cur.fetchall()

    # one entry per person, in the format family-chart expects
    tree = {}
    for p in people:
        tree[p["id"]] = {
            "id": p["id"],
            "data": {
                "first name": p["forenames"] or "",
                "last name": p["surname"] or "",
                "birthday": "" if p["birth"] is None else str(p["birth"]),
                "years": years_text(p["birth"], p["death"]),
                "gender": "",
            },
            "rels": {"parents": [], "spouses": [], "children": []},
        }

    # group the children by family
    kids = {}
    for link in links:
        kids.setdefault(link["family_id"], []).append(link["child_id"])

    # fill in the relationships from each family
    for fam in families:
        dad = fam["father_id"]
        mum = fam["mother_id"]

        # the data has no gender column, so we use the family role
        if dad:
            tree[dad]["data"]["gender"] = "M"
        if mum:
            tree[mum]["data"]["gender"] = "F"

        if dad and mum:
            tree[dad]["rels"]["spouses"].append(mum)
            tree[mum]["rels"]["spouses"].append(dad)

        for child in kids.get(fam["id"], []):
            for parent in (dad, mum):
                if parent:
                    tree[child]["rels"]["parents"].append(parent)
                    tree[parent]["rels"]["children"].append(child)

    return jsonify(list(tree.values()))


if __name__ == "__main__":
    app.run(debug=True)