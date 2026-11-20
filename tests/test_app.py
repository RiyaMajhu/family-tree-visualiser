import pytest

from app import app

# IDs of people used in the tests
ELIZABETH = "@I122593541858@"      # Elizabeth Anne Wickham
THOMAS = "@I122596874619@"         # Thomas Huxtable, married twice
MARY = "@I122628820256@"           # Mary Philcox, Thomas's first wife
BENEBA = "@I122596874628@"         # Beneba Peddlesden, Thomas's second wife
LEVI_THOMAS = "@I122617894613@"    # Levi Thomas Huxtable, son of Thomas and Beneba


@pytest.fixture
def client():
    # Flask's test client lets us visit pages without running the real server
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture(scope="module")
def tree():
    # get the full tree data once and share it between the tests
    app.config["TESTING"] = True
    response = app.test_client().get("/api/tree")
    return {person["id"]: person for person in response.get_json()}


# ---------- the main page ----------

def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Family Tree" in response.data


# ---------- the /person route ----------

def test_person_returns_their_parents(client):
    data = client.get(f"/person/{ELIZABETH}").get_json()
    parent_names = {p["forenames"] for p in data["parents"]}
    assert parent_names == {"Wilfred David", "Dorothy Margaret"}


def test_person_with_two_marriages_has_two_partnerships(client):
    data = client.get(f"/person/{THOMAS}").get_json()
    partner_ids = {p["partner"]["id"] for p in data["partnerships"]}
    assert partner_ids == {MARY, BENEBA}


def test_unknown_person_gives_404(client):
    response = client.get("/person/@NOT_A_REAL_ID@")
    assert response.status_code == 404


# ---------- the /api/tree route ----------

def test_tree_has_everyone(tree):
    assert len(tree) == 9029


def test_tree_entries_have_the_right_format(tree):
    for person in tree.values():
        assert set(person.keys()) == {"id", "data", "rels"}
        assert set(person["rels"].keys()) == {"parents", "spouses", "children"}
        assert person["data"]["gender"] in ("M", "F", "")


def test_tree_links_all_point_to_real_people(tree):
    for person in tree.values():
        for relation in ("parents", "spouses", "children"):
            for other_id in person["rels"][relation]:
                assert other_id in tree


def test_tree_links_go_both_ways(tree):
    # if A lists B as a child, B should list A as a parent (and the same for spouses)
    for person_id, person in tree.items():
        for child in person["rels"]["children"]:
            assert person_id in tree[child]["rels"]["parents"]
        for spouse in person["rels"]["spouses"]:
            assert person_id in tree[spouse]["rels"]["spouses"]


def test_remarriage_shows_both_spouses(tree):
    assert set(tree[THOMAS]["rels"]["spouses"]) == {MARY, BENEBA}


def test_child_is_linked_to_the_right_mother(tree):
    parents = tree[LEVI_THOMAS]["rels"]["parents"]
    assert THOMAS in parents
    assert BENEBA in parents
    assert MARY not in parents


def test_years_text(tree):
    assert tree[THOMAS]["data"]["years"] == "1848 - 1927"