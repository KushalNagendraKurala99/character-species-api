
# db.py
from pymongo import MongoClient
import os

# Use environment variable if set, otherwise fallback to your Atlas URI
MONGO_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://Kkn_DBuser:DataK%4099@cluster0.ahuh6sb.mongodb.net/starwar?retryWrites=true&w=majority&appName=Cluster0"
)

client = MongoClient(MONGO_URI)
db = client.get_database("starwar")

# Collections
characters = db["characters"]
species = db["species"]
