from flask import Flask, request, jsonify
from ariadne import QueryType, MutationType, make_executable_schema, graphql_sync
from ariadne.explorer import ExplorerGraphiQL
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

# --- MongoDB Atlas connection ---
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "Your URI"
)
client = MongoClient(MONGODB_URI)
db = client["starwar"]
characters = db["characters"]
species = db["species"]

# --- GraphQL schema ---
type_defs = """
    type Character {
        id: ID!
        name: String
        height: String
        species: String
    }

    type Species {
        id: ID!
        name: String
        classification: String
        language: String
    }

    type Query {
        character(id: ID!): Character
        characters(name: String): [Character]
        species(id: ID!): Species
        allSpecies(name: String): [Species]
    }

    type Mutation {
        createCharacter(name: String!, height: String, species: String): Character
        updateCharacter(id: ID, name: String, height: String, species: String): Character
        deleteCharacter(id: ID, name: String): Boolean

        createSpecies(name: String!, classification: String, language: String): Species
        updateSpecies(id: ID, name: String, classification: String, language: String): Species
        deleteSpecies(id: ID, name: String): Boolean
    }
"""

query = QueryType()
mutation = MutationType()

# --- Character Queries ---
@query.field("character")
def resolve_character(_, info, id):
    doc = characters.find_one({"_id": ObjectId(id)})
    if doc:
        doc["id"] = str(doc["_id"])
        return doc
    return None

@query.field("characters")
def resolve_characters(_, info, name=None):
    q = {}
    if name:
        q["name"] = {"$regex": name, "$options": "i"}
    docs = characters.find(q)
    return [{**d, "id": str(d["_id"])} for d in docs]

# --- Species Queries ---
@query.field("species")
def resolve_species(_, info, id):
    doc = species.find_one({"_id": ObjectId(id)})
    if doc:
        doc["id"] = str(doc["_id"])
        return doc
    return None

@query.field("allSpecies")
def resolve_all_species(_, info, name=None):
    q = {}
    if name:
        q["name"] = {"$regex": name, "$options": "i"}
    docs = species.find(q)
    return [{**d, "id": str(d["_id"])} for d in docs]

# --- Character Mutations ---
@mutation.field("createCharacter")
def resolve_create_character(_, info, name, height=None, species=None):
    doc = {"name": name}
    if height:
        doc["height"] = height
    if species:
        doc["species"] = species
    res = characters.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    return doc

@mutation.field("updateCharacter")
def resolve_update_character(_, info, id=None, name=None, height=None, species=None):
    query = {}
    if id:
        query["_id"] = ObjectId(id)
    elif name:
        query["name"] = name
    else:
        return None
    
    update_fields = {}
    if height:
        update_fields["height"] = height
    if species:
        update_fields["species"] = species
    if name:
        update_fields["name"] = name

    if not update_fields:
        return None

    res = characters.find_one_and_update(
        query,
        {"$set": update_fields},
        return_document=True
    )
    if res:
        res["id"] = str(res["_id"])
    return res

@mutation.field("deleteCharacter")
def resolve_delete_character(_, info, id=None, name=None):
    query = {}
    if id:
        query["_id"] = ObjectId(id)
    elif name:
        query["name"] = name
    else:
        return False
    result = characters.delete_one(query)
    return result.deleted_count > 0

# --- Species Mutations ---
@mutation.field("createSpecies")
def resolve_create_species(_, info, name, classification=None, language=None):
    doc = {"name": name}
    if classification:
        doc["classification"] = classification
    if language:
        doc["language"] = language
    res = species.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    return doc

@mutation.field("updateSpecies")
def resolve_update_species(_, info, id=None, name=None, classification=None, language=None):
    query = {}
    if id:
        query["_id"] = ObjectId(id)
    elif name:
        query["name"] = name
    else:
        return None

    update_fields = {}
    if classification:
        update_fields["classification"] = classification
    if language:
        update_fields["language"] = language
    if name:
        update_fields["name"] = name

    if not update_fields:
        return None

    res = species.find_one_and_update(
        query,
        {"$set": update_fields},
        return_document=True
    )
    if res:
        res["id"] = str(res["_id"])
    return res

@mutation.field("deleteSpecies")
def resolve_delete_species(_, info, id=None, name=None):
    query = {}
    if id:
        query["_id"] = ObjectId(id)
    elif name:
        query["name"] = name
    else:
        return False
    result = species.delete_one(query)
    return result.deleted_count > 0

# --- Schema setup ---
schema = make_executable_schema(type_defs, query, mutation)

app = Flask(__name__)
explorer_html = ExplorerGraphiQL().html(None)

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return explorer_html, 200

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=True)
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    app.run(debug=True, port=5000)
