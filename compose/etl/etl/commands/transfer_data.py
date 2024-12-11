from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import elasticsearch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from etl.extract import (
    FilmWorksExtractor,
    FilmWorksParser,
)
from etl.load import FilmsLoader
from etl.settings import settings
from etl.state import JsonFileStorage
from etl.transform import FilmsTransformer
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

        with open(BASE_DIR / 'schema' / 'films.json', 'rb') as films_index_file:
            films_index_json = films_index_file.read().decode()

        films_index_data: dict = json.loads(films_index_json)
        films_loader = FilmsLoader(
            client=elasticsearch_client,
            index_data=films_index_data,
        )

        while True:
            film_works = film_works_extractor.extract(
                last_modified=state.extractors.film_works.last_modified,
            )

            film_works_parser = FilmWorksParser(film_works=film_works)
            films_transformer = FilmsTransformer()
            film_works_parser.parse(visitor=films_transformer)

            films_transform_result = films_transformer.get_result()

            if films_transform_result.films:
                films_loader.load(films=films_transform_result.films)
                state.extractors.film_works.last_modified = films_transform_result.last_modified
                storage.save(state)
            else:
                time.sleep(10)


if __name__ == '__main__':
    main()
