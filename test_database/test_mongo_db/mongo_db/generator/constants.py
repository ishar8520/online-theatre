import os

from dotenv import load_dotenv

load_dotenv()

BATCH_SIZE = 100_000
TOTAL_GENERATE_DATA = 1_000_000
QUANTITY_USERS = 100_000
QUANTITY_MOVIES = 1000
MAX_REVIEW_LEN = 200

MONGO_NAME = "mongodb"


MONGO_DSL = {
    "host": os.environ.get("MONGO_HOST", "localhost"),
    "port": int(os.environ.get("MONGO_PORT", 27017)),
    "username": os.environ.get("MONGO_USER", "admin"),
    "password": os.environ.get("MONGO_PASSWORD", "admin_password"),
    "authSource": os.environ.get("MONGO_AUTH_SOURCE", "admin"),
    "connectTimeoutMS": 30000,
    "socketTimeoutMS": 30000,
    "serverSelectionTimeoutMS": 30000,
    "retryWrites": True,
    "retryReads": True,
}