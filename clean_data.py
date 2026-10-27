import pandas as pd

people = pd.read_excel("data/FamilyTree.xlsx", sheet_name="People")

# remove the extra spaces from all the text
people = people.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

# turn the years into proper numbers (blank if missing)
for col in ["Birth", "Death", "Marriage"]:
    people[col] = pd.to_numeric(people[col], errors="coerce").astype("Int64")

print(people.head(10))
print(people.dtypes)

families = pd.read_excel("data/FamilyTree.xlsx", sheet_name="Families")

# remove extra spaces from all the text
families = families.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

# every column after Father and Mother is a child column
child_cols = families.columns[3:]

# turn the child columns into one list of (family, child) pairs
children = families.melt(id_vars="Family", value_vars=child_cols, value_name="Child")
children = children.dropna(subset=["Child"])[["Family", "Child"]]

# keep just the family, father and mother in the families table
families = families[["Family", "Father", "Mother"]]

print(families.head())
print(children.head(10))
print(len(families), "families and", len(children), "parent-child links")

people_ids = set(people["Id"])
family_ids = set(families["Family"])

# every parent and child should be a real person
missing_fathers = families["Father"].dropna()[~families["Father"].dropna().isin(people_ids)]
missing_mothers = families["Mother"].dropna()[~families["Mother"].dropna().isin(people_ids)]
missing_children = children[~children["Child"].isin(people_ids)]

# every Parents family in People should be a real family
parent_fams = people["Parents"].dropna()
missing_parent_fams = parent_fams[~parent_fams.isin(family_ids)]

print("Fathers not found:", len(missing_fathers))
print("Mothers not found:", len(missing_mothers))
print("Children not found:", len(missing_children))
print("Parents families not found:", len(missing_parent_fams))