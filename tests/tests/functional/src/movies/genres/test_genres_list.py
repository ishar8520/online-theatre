from __future__ import annotations

from collections.abc import Iterable
from urllib.parse import urljoin

import aiohttp
import pytest

from ....settings import settings
from ....utils.api import models as api_models
from ....utils.elasticsearch import ElasticsearchIndex
from ....utils.elasticsearch.models import Genre
from ....utils.redis import RedisCache


class GenresListTestRunner:
    redis_cache: RedisCache
    elasticsearch_index: ElasticsearchIndex[Genre]
    aiohttp_session: aiohttp.ClientSession

    genres_list_api_url: str

    def __init__(self,
                 *,
                 redis_cache: RedisCache,
                 elasticsearch_index: ElasticsearchIndex[Genre],
                 aiohttp_session: aiohttp.ClientSession) -> None:
        self.elasticsearch_index = elasticsearch_index
        self.aiohttp_session = aiohttp_session
        self.redis_cache = redis_cache

        self.genres_list_api_url = urljoin(settings.movies_api_url, 'v1/genres/')

    async def run(self) -> None:
        raise NotImplementedError

    def _generate_genres(self, *, count: int = 1) -> Iterable[Genre]:
        for i in range(1, count + 1):
            yield Genre(name=f'Жанр {i}')


class GenresListEmptyTestRunner(GenresListTestRunner):
    async def run(self) -> None:
        async with self.aiohttp_session.get(self.genres_list_api_url) as response:
            assert response.status == 200
            genres_results: list[dict] = await response.json()

        assert genres_results == []


class GenresListSinglePageTestRunner(GenresListTestRunner):
    async def run(self) -> None:
        genres = list(self._generate_genres(count=10))
        await self.elasticsearch_index.load_documents(documents=genres)

        async with self.aiohttp_session.get(self.genres_list_api_url) as response:
            assert response.status == 200
            genres_results: list[dict] = await response.json()

        genres_results_dict: dict[str, dict] = {
            genre_result_data['uuid']: genre_result_data for genre_result_data in genres_results
        }

        expected_genres_results_dict: dict[str, dict] = {}
        for genre in genres:
            expected_genre_result = api_models.Genre(**genre.model_dump())
            expected_genre_result_data = expected_genre_result.model_dump(mode='json', by_alias=True)
            expected_genres_results_dict[expected_genre_result_data['uuid']] = expected_genre_result_data

        assert genres_results_dict == expected_genres_results_dict


class GenresListMultiplePagesTestRunner(GenresListTestRunner):
    async def run(self) -> None:
        genres_count = 25
        page_size = 10
        pages_count = genres_count // page_size + 1

        genres = list(self._generate_genres(count=25))
        await self.elasticsearch_index.load_documents(documents=genres)

        genres_results: list[dict] = []

        for page_number in range(1, pages_count + 1):
            async with self.aiohttp_session.get(self.genres_list_api_url, params={
                'page_size': page_size,
                'page_number': page_number,
            }) as response:
                assert response.status == 200
                genres_results += await response.json()

        genres_results_dict: dict[str, dict] = {
            genre_result_data['uuid']: genre_result_data for genre_result_data in genres_results
        }

        expected_genres_results_dict: dict[str, dict] = {}
        for genre in genres:
            expected_genre_result = api_models.Genre(**genre.model_dump())
            expected_genre_result_data = expected_genre_result.model_dump(mode='json', by_alias=True)
            expected_genres_results_dict[expected_genre_result_data['uuid']] = expected_genre_result_data

        assert genres_results_dict == expected_genres_results_dict


@pytest.mark.asyncio(loop_scope='session')
async def test_genres_list_empty(
        redis_cache,
        create_elasticsearch_index,
        aiohttp_session,
) -> None:
    elasticsearch_index = await create_elasticsearch_index(index_name='genres')

    await GenresListEmptyTestRunner(
        redis_cache=redis_cache,
        elasticsearch_index=elasticsearch_index,
        aiohttp_session=aiohttp_session,
    ).run()


@pytest.mark.asyncio(loop_scope='session')
async def test_genres_list_single_page(
        redis_cache,
        create_elasticsearch_index,
        aiohttp_session,
) -> None:
    elasticsearch_index = await create_elasticsearch_index(index_name='genres')

    await GenresListSinglePageTestRunner(
        redis_cache=redis_cache,
        elasticsearch_index=elasticsearch_index,
        aiohttp_session=aiohttp_session,
    ).run()


@pytest.mark.asyncio(loop_scope='session')
async def test_genres_list_multiple_pages(
        redis_cache,
        create_elasticsearch_index,
        aiohttp_session,
) -> None:
    elasticsearch_index = await create_elasticsearch_index(index_name='genres')

    await GenresListMultiplePagesTestRunner(
        redis_cache=redis_cache,
        elasticsearch_index=elasticsearch_index,
        aiohttp_session=aiohttp_session,
    ).run()
