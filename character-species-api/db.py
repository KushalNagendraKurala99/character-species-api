
# db.py
from pymongo import MongoClient
import os

# Use environment variable if set, otherwise fallback to your Atlas URI
MONGO_URI = os.getenv(
    "MONGODB_URI",
    "Your uri"
)

client = MongoClient(MONGO_URI)
db = client.get_database("starwar")

# Collections
characters = db["characters"]
species = db["species"]
