import pandas as pd

FILE = "data/FamilyTree.xlsx"


def clean_text(col):
    # remove extra spaces from text columns, leave other columns alone
    if pd.api.types.is_object_dtype(col) or pd.api.types.is_string_dtype(col):
        return col.str.strip()
    return col


def load_clean_data():
    # people
    people = pd.read_excel(FILE, sheet_name="People")
    people = people.apply(clean_text)
    for col in ["Birth", "Death", "Marriage"]:
        people[col] = pd.to_numeric(people[col], errors="coerce").astype("Int64")

    # families
    families = pd.read_excel(FILE, sheet_name="Families")
    families = families.apply(clean_text)
    child_cols = families.columns[3:]
    children = families.melt(id_vars="Family", value_vars=child_cols, value_name="Child")
    children = children.dropna(subset=["Child"])[["Family", "Child"]]
    families = families[["Family", "Father", "Mother"]]

    return people, families, children


if __name__ == "__main__":
    people, families, children = load_clean_data()

    people_ids = set(people["Id"])
    family_ids = set(families["Family"])

    missing_fathers = families["Father"].dropna()[~families["Father"].dropna().isin(people_ids)]
    missing_mothers = families["Mother"].dropna()[~families["Mother"].dropna().isin(people_ids)]
    missing_children = children[~children["Child"].isin(people_ids)]
    parent_fams = people["Parents"].dropna()
    missing_parent_fams = parent_fams[~parent_fams.isin(family_ids)]

    print(len(people), "people,", len(families), "families,", len(children), "parent-child links")
    print("Fathers not found:", len(missing_fathers))
    print("Mothers not found:", len(missing_mothers))
    print("Children not found:", len(missing_children))
    print("Parents families not found:", len(missing_parent_fams))