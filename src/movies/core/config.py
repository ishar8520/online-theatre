import os
from logging import config as logging_config

from .logger import LOGGING

logging_config.dictConfig(LOGGING)

PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_CACHE_EXPIRE_IN_SECONDS = 60 * 5

ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))

ELASTIC_INDEX_NAME_FILMS = 'films'
ELASTIC_INDEX_NAME_GENRES = 'genres'
ELASTIC_INDEX_NAME_PERSONS = 'persons'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
