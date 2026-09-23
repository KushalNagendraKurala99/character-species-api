from flask import Flask, request, jsonify
from bson import ObjectId
from pymongo import MongoClient
import re
import os

app = Flask(__name__)

# --- MongoDB Atlas connection ---
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://Kkn_DBuser:DataK%4099@cluster0.ahuh6sb.mongodb.net/starwar?retryWrites=true&w=majority&appName=Cluster0"
)
client = MongoClient(MONGODB_URI)
db = client["starwar"]

# Helper: Convert ObjectId to string
def convert_objectid(obj):
    if isinstance(obj, list):
        return [convert_objectid(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj

# --- Human-friendly LLM parser ---
def parse_llm_command(command: str):
    command = command.strip().lower()

    # --- Map singular → plural collection names ---
    collection_map = {
        "character": "characters",
        "characters": "characters",
        "species": "species"   # no extra 's'
    }

    # --- FIND ALL ---
    match = re.search(r'find all (characters|species)', command)
    if match:
        collection = collection_map[match.group(1)]
        return {"find": {"collection": collection, "filter": {}}}

    # --- FIND ONE ---
    match = re.search(r'find (?:the )?(character|species) named (.+)', command)
    if match:
        collection = collection_map[match.group(1)]
        name = match.group(2).strip().title()
        return {"find": {"collection": collection, "filter": {"name": name}}}

    # --- INSERT ---
    match = re.search(r'insert (?:a )?(character|species) named (.+?)(?: with (.+))?$', command)
    if match:
        collection = collection_map[match.group(1)]
        name = match.group(2).strip().title()
        doc = {"name": name}
        if match.group(3):
            parts = re.split(r'\band\b|,', match.group(3))
            for part in parts:
                kv = part.strip().split(' ', 1)
                if len(kv) == 2:
                    key = kv[0].strip().lower()
                    value = kv[1].strip()
                    if value.isdigit():
                        value = int(value)
                    else:
                        value = value.title()
                    doc[key] = value
        return {"insert": {"collection": collection, "document": doc}}

    # --- UPDATE ---
    match = re.search(r'update (?:the )?(\w+) of (?:the )?(character|species) (.+) to (.+)', command)
    if match:
        field = match.group(1).lower()
        collection = collection_map[match.group(2)]
        name = match.group(3).strip().title()
        value = match.group(4).strip()

        if value.isdigit():
            value = int(value)

        return {
            "update": {
                "collection": collection,
                "filter": {"name": name},
                "update": {"$set": {field: value}}
            }
        }

    # --- DELETE ---
    match = re.search(r'delete (?:the )?(character|species) (.+)', command)
    if match:
        collection = collection_map[match.group(1)]
        name = match.group(2).strip().title()
        return {"delete": {"collection": collection, "filter": {"name": name}}}

    return None


# --- NLP Handler ---
@app.route("/nlp", methods=["POST"])
def nlp_handler():
    try:
        payload = request.get_json(force=True)

        # Natural language command support
        if "llm_command" in payload:
            llm_payload = parse_llm_command(payload["llm_command"])
            if llm_payload:
                payload = llm_payload
            else:
                return jsonify({"error": "Could not parse LLM command"}), 400

        # --- FIND ---
        if "find" in payload:
            coll = db[payload["find"]["collection"]]
            result = list(coll.find(payload["find"].get("filter", {})))
            result = convert_objectid(result)
            return jsonify({"operation": "find", "raw": payload, "result": result})

        # --- UPDATE ---
        elif "update" in payload:
            coll = db[payload["update"]["collection"]]
            res = coll.update_many(payload["update"].get("filter", {}), payload["update"].get("update"))
            return jsonify({
                "operation": "update",
                "matched_count": res.matched_count,
                "modified_count": res.modified_count
            })

        # --- INSERT ---
        elif "insert" in payload:
            coll = db[payload["insert"]["collection"]]
            res = coll.insert_one(payload["insert"]["document"])
            return jsonify({"operation": "insert", "inserted_id": str(res.inserted_id)})

        # --- DELETE ---
        elif "delete" in payload:
            coll = db[payload["delete"]["collection"]]
            res = coll.delete_many(payload["delete"]["filter"])
            return jsonify({"operation": "delete", "deleted_count": res.deleted_count})

        else:
            return jsonify({"error": "No valid operation found"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5010)
