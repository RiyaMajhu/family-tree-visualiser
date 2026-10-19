import pandas as pd

people = pd.read_excel("data/FamilyTree.xlsx", sheet_name="People")
families = pd.read_excel("data/FamilyTree.xlsx", sheet_name="Families")

print(people.head())
print(families.head())
print(len(people), "people and", len(families), "families")