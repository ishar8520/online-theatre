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
    GenresExtractor,
    GenresParser,
)
from etl.load import ElasticsearchLoader

from etl.settings import settings
from etl.state import JsonFileStorage
from etl.transform import (
    Film,
    Genre,
    FilmsTransformer,
    GenresTransformer,
)
from etl.utils import setup_logging


def main() -> None:
    setup_logging(filename=BASE_DIR / 'logs' / 'transfer_data.log')
    postgresql_connection_params = settings.postgresql.get_connection_params()
    schema_dir = BASE_DIR / 'schema'

    storage = JsonFileStorage(file_path=BASE_DIR / 'data' / 'state.json')
    state = storage.load()

    with (
        elasticsearch.Elasticsearch(settings.elasticsearch.url) as elasticsearch_client,
    ):
        film_works_extractor = FilmWorksExtractor(connection_params=postgresql_connection_params)

        with open(schema_dir / 'films.json', 'rb') as films_index_file:
            films_index_json = films_index_file.read().decode()

        films_index_data: dict = json.loads(films_index_json)
        films_loader = ElasticsearchLoader[Film](
            client=elasticsearch_client,
            index_name='films',
            index_data=films_index_data,
        )

        genres_extractor = GenresExtractor(connection_params=postgresql_connection_params)

        with open(schema_dir / 'genres.json', 'rb') as genres_index_file:
            genres_index_json = genres_index_file.read().decode()

        genres_index_data: dict = json.loads(genres_index_json)
        genres_loader = ElasticsearchLoader[Genre](
            client=elasticsearch_client,
            index_name='genres',
            index_data=genres_index_data,
        )

        while True:
            while True:
                film_works = film_works_extractor.extract(
                    last_modified=state.extractors.film_works.last_modified,
                )

                film_works_parser = FilmWorksParser(film_works=film_works)
                films_transformer = FilmsTransformer()
                film_works_parser.parse(visitor=films_transformer)
                films_transform_result = films_transformer.get_result()

                if not films_transform_result.films:
                    break

                films_loader.load(documents=films_transform_result.films)
                state.extractors.film_works.last_modified = films_transform_result.last_modified
                storage.save(state)

            while True:
                genres = genres_extractor.extract(
                    last_modified=state.extractors.genres.last_modified,
                )

                genres_parser = GenresParser(genres=genres)
                genres_transformer = GenresTransformer()
                genres_parser.parse(visitor=genres_transformer)
                genres_transform_result = genres_transformer.get_result()

                if not genres_transform_result.genres:
                    break

                genres_loader.load(documents=genres_transform_result.genres)
                state.extractors.genres.last_modified = genres_transform_result.last_modified
                storage.save(state)

            time.sleep(10)


if __name__ == '__main__':
    main()
