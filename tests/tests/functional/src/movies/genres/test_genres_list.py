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

    def _create_genres(self, *, count: int = 1) -> Iterable[Genre]:
        for i in range(1, count + 1):
            yield Genre(name=f'Жанр {i}')


class GenresListEmptyTestRunner(GenresListTestRunner):
    async def run(self) -> None:
        async with self.aiohttp_session.get(self.genres_list_api_url) as response:
            assert response.status == 200
            api_genres: list[dict] = await response.json()

        assert api_genres == []


class GenresListSinglePageTestRunner(GenresListTestRunner):
    async def run(self) -> None:
        genres = list(self._create_genres(count=10))
        await self.elasticsearch_index.load_documents(documents=genres)

        async with self.aiohttp_session.get(self.genres_list_api_url) as response:
            assert response.status == 200
            api_genres: list[dict] = await response.json()

        api_genres_dict = {api_genre_data['uuid']: api_genre_data for api_genre_data in api_genres}

        expected_api_genres_dict = {}
        for genre in genres:
            expected_api_genre = api_models.Genre(**genre.model_dump())
            expected_api_genre_data = expected_api_genre.model_dump(mode='json', by_alias=True)
            expected_api_genres_dict[expected_api_genre_data['uuid']] = expected_api_genre_data

        assert api_genres_dict == expected_api_genres_dict


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
