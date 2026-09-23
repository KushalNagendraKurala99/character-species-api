# test_db.py
from db import characters, species

print("Characters count:", characters.count_documents({}))
print("One character:", characters.find_one({}))

print("Species count:", species.count_documents({}))
print("One species:", species.find_one({}))
