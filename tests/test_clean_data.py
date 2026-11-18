import pandas as pd
import pytest

from clean_data import clean_text, load_clean_data


# ---------- tests for clean_text on small made-up columns ----------

def test_removes_extra_spaces():
    col = pd.Series(["Fancy ", " Wickham", "  Elizabeth Anne  "])
    result = clean_text(col)
    assert list(result) == ["Fancy", "Wickham", "Elizabeth Anne"]


def test_leaves_number_columns_alone():
    col = pd.Series([1959, 1930, 2022])
    result = clean_text(col)
    assert list(result) == [1959, 1930, 2022]


def test_keeps_blank_cells_blank():
    col = pd.Series(["Fancy ", None])
    result = clean_text(col)
    assert result[0] == "Fancy"
    assert pd.isna(result[1])


# ---------- tests on the real cleaned data ----------

@pytest.fixture(scope="module")
def data():
    # load the data once and share it between the tests below
    return load_clean_data()


def test_correct_number_of_rows(data):
    people, families, children = data
    assert len(people) == 9029
    assert len(families) == 4720
    assert len(children) == 5357


def test_years_are_numbers(data):
    people, _, _ = data
    for col in ["Birth", "Death", "Marriage"]:
        assert people[col].dtype == "Int64"


def test_no_extra_spaces_in_names(data):
    people, _, _ = data
    for col in ["Forenames", "Surname"]:
        names = people[col].dropna()
        assert (names == names.str.strip()).all()


def test_families_only_have_three_columns(data):
    _, families, _ = data
    assert list(families.columns) == ["Family", "Father", "Mother"]


def test_every_parent_and_child_is_a_real_person(data):
    people, families, children = data
    people_ids = set(people["Id"])
    assert families["Father"].dropna().isin(people_ids).all()
    assert families["Mother"].dropna().isin(people_ids).all()
    assert children["Child"].isin(people_ids).all()


def test_every_child_link_points_to_a_real_family(data):
    _, families, children = data
    assert children["Family"].isin(set(families["Family"])).all()