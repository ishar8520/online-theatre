from __future__ import annotations

import sys
import time
from pathlib import Path

import elasticsearch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from etl.extract import (
    FilmWorksExtractor,
    GenresExtractor,
)
from etl.load import ElasticsearchLoader
from etl.pipelines import (
    ETLPipeline,
    FilmsTransformExecutor,
    GenresTransformExecutor,
)
from etl.settings import settings
from etl.state import JsonFileStorage
from etl.transform import (
    Film,
    Genre,
)
from etl.utils import (
    setup_logging,
    load_index_file,
)


def main() -> None:
    setup_logging(file_path=BASE_DIR / 'logs' / 'transfer_data.log')
    postgresql_connection_params = settings.postgresql.get_connection_params()
    schema_dir = BASE_DIR / 'schema'

    storage = JsonFileStorage(file_path=BASE_DIR / 'data' / 'state.json')
    state = storage.load()

    with (
        elasticsearch.Elasticsearch(settings.elasticsearch.url) as elasticsearch_client,
    ):
        films_pipeline = ETLPipeline[Film](
            extractor=FilmWorksExtractor(connection_params=postgresql_connection_params),
            transform_executor=FilmsTransformExecutor(),
            loader=ElasticsearchLoader[Film](
                client=elasticsearch_client,
                index_name='films',
                index_data=load_index_file(schema_dir / 'films.json'),
            ),
        )

        genres_pipeline = ETLPipeline[Genre](
            extractor=GenresExtractor(connection_params=postgresql_connection_params),
            transform_executor=GenresTransformExecutor(),
            loader=ElasticsearchLoader[Genre](
                client=elasticsearch_client,
                index_name='genres',
                index_data=load_index_file(schema_dir / 'genres.json'),
            ),
        )

        while True:
            for etl_pipeline, extractor_state in [
                (films_pipeline, state.extractors.film_works),
                (genres_pipeline, state.extractors.genres),
            ]:
                while True:
                    documents_transform_result = etl_pipeline.transfer_data(
                        last_modified=extractor_state.last_modified,
                    )

                    if not documents_transform_result.documents:
                        break

                    extractor_state.last_modified = documents_transform_result.last_modified
                    storage.save(state)

            time.sleep(10)


if __name__ == '__main__':
    main()
