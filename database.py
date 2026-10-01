import os

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017"
)

client = MongoClient(MONGODB_URI)

db = client["travel_db"]

hotels_collection = db["hotels"]


def get_database():
    return db


def get_hotels_collection():
    return hotels_collection