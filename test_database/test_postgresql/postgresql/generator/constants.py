import os

from dotenv import load_dotenv

load_dotenv()

BATCH_SIZE = 100_000
TOTAL_GENERATE_DATA = 1_000_000
QUANTITY_USERS = 100_000
QUANTITY_MOVIES = 1000
MAX_REVIEW_LEN = 200


DSL = {
    "dbname": os.environ.get("POSTGRES_DB"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
    "host": os.environ.get("POSTGRES_HOST"),
    "port": os.environ.get("POSTGRES_PORT"),
}
