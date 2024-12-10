from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

import elasticsearch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from etl.extract import (
    FilmWorksExtractor,
    FilmWorksParser,
    JsonFileStorage,
)
from etl.load import MoviesLoader
from etl.settings import settings
from etl.transform import MoviesTransformer
from etl.utils import setup_logging


def main() -> None:
    setup_logging(filename=BASE_DIR / 'logs' / 'transfer_data.log')
    postgresql_connection_params = settings.postgresql.get_connection_params()

    storage = JsonFileStorage(file_path=BASE_DIR / 'data' / 'state.json')
    state = storage.load()

    with (
        elasticsearch.Elasticsearch(settings.elasticsearch.url) as elasticsearch_client,
    ):
        film_works_extractor = FilmWorksExtractor(connection_params=postgresql_connection_params)

        with open(BASE_DIR / 'schema' / 'movies.json', 'rb') as movies_index_file:
            movies_index_json = movies_index_file.read().decode()

        movies_index_data: dict = json.loads(movies_index_json)
        movies_loader = MoviesLoader(
            client=elasticsearch_client,
            index_data=movies_index_data,
        )

        while True:
            film_works = film_works_extractor.extract(last_modified=state.last_modified)

            film_works_parser = FilmWorksParser(film_works=film_works)
            movies_transformer = MoviesTransformer()
            film_works_parser.parse(visitor=movies_transformer)

            movies_transform_result = movies_transformer.get_result()

            if movies_transform_result.movies:
                movies_loader.load(movies=movies_transform_result.movies)
                state.last_modified = movies_transform_result.last_modified
                storage.save(state)
            else:
                time.sleep(10)


if __name__ == '__main__':
    main()
