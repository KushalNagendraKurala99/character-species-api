from db import characters, species

def normalize_species():
    chars = characters.find()
    for c in chars:
        if "species" in c:
            sp_name = c["species"]
            sp = species.find_one({"name": sp_name})
            if not sp:
                res = species.insert_one({"name": sp_name})
                sp_id = res.inserted_id
            else:
                sp_id = sp["_id"]
            characters.update_one({"_id": c["_id"]}, {"$set": {"species_id": sp_id}})
    print("✅ Normalization complete")

if __name__ == "__main__":
    normalize_species()
