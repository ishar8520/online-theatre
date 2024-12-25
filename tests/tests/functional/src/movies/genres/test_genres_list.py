from __future__ import annotations

import uuid
from collections.abc import Iterable
from urllib.parse import urljoin

import aiohttp
import pytest

from ....settings import settings
from ....utils.elasticsearch import ElasticsearchIndex
from ....utils.redis import RedisCache


def create_genres(*, count: int = 1) -> Iterable[dict]:
    for i in range(1, count + 1):
        yield {
            'id': uuid.uuid4(),
            'name': f'Жанр {i}',
        }


class GenresListTestRunner:
    redis_cache: RedisCache
    elasticsearch_index: ElasticsearchIndex
    aiohttp_session: aiohttp.ClientSession

    genres_list_api_url: str

    def __init__(self,
                 *,
                 redis_cache: RedisCache,
                 elasticsearch_index: ElasticsearchIndex,
                 aiohttp_session: aiohttp.ClientSession) -> None:
        self.elasticsearch_index = elasticsearch_index
        self.aiohttp_session = aiohttp_session
        self.redis_cache = redis_cache

        self.genres_list_api_url = urljoin(settings.movies_api_url, 'v1/genres/')

    async def run(self) -> None:
        raise NotImplementedError


class GenresListEmptyTestRunner(GenresListTestRunner):
    async def run(self) -> None:
        async with self.aiohttp_session.get(self.genres_list_api_url) as response:
            assert response.status == 200
            results_list: list[dict] = await response.json()

        assert results_list == []


class GenresListSinglePageTestRunner(GenresListTestRunner):
    async def run(self) -> None:
        genres = list(create_genres(count=10))
        await self.elasticsearch_index.load_data(documents=genres)

        async with self.aiohttp_session.get(self.genres_list_api_url) as response:
            assert response.status == 200
            results_list: list[dict] = await response.json()

        results_dict = {genre_result['uuid']: genre_result for genre_result in results_list}
        expected_results_dict = {str(genre_data['id']): {
            'uuid': str(genre_data['id']),
            'name': genre_data['name'],
        } for genre_data in genres}
        assert results_dict == expected_results_dict


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
