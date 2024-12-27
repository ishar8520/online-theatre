import random
import uuid
from urllib.parse import urljoin

import pytest

from ...settings import settings
from ...utils.elasticsearch.models import (
    Film,
    FilmGenre,
)

INDEX_NAME_FILM = 'films'


@pytest.mark.parametrize(
    "count, input, expected",
    [
        (
            10,
            {},
            {'status': 200, 'length': 10}
        ),
        (
            100,
            {'page_size': 100},
            {'status': 200, 'length': 50}
        ),
        (
            10,
            {'page_number': -1},
            {'status': 200, 'length': 10}
        ),
        (
            10,
            {'page_number': 5},
            {'status': 200, 'length': 0}
        ),
        (
            10,
            {'page_number': 'string'},
            {'status': 422, 'length': None}
        ),
        (
            10,
            {'page_size': 'string'},
            {'status': 422, 'length': None}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_get_list_pagination(
        create_elasticsearch_index,
        aiohttp_session,
        count: int,
        input,
        expected
):

    def films_generator():
        for i in range(count):
            yield Film(
                title=f'The star. Episode {i}',
                description=f'Description {i}',
                rating=round(random.uniform(1.0, 10.0), 1),
            )

    elastic = await create_elasticsearch_index(index_name=INDEX_NAME_FILM)
    await elastic.load_documents(documents=films_generator())

    url = urljoin(settings.movies_api_v1_url, 'films/')
    async with aiohttp_session.get(url, params=input) as response:
        status = response.status
        data = await response.json()

        assert status == expected['status']

        if expected['length']:
            assert len(data) == expected['length']


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            {'sort': '-imdb_rating'},
            {'status': 200, 'rating': 10}
        ),
        (
            {'sort': 'imdb_rating'},
            {'status': 200, 'rating': 2}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_get_list_sort(
        create_elasticsearch_index,
        aiohttp_session,
        input,
        expected
):
    films = [
        Film(
            title='The star. Episode 1',
            description='Description',
            rating=10,
        ),
        Film(
            title='The star. Episode 2',
            description='Description',
            rating=2,
        )
    ]

    elastic = await create_elasticsearch_index(index_name=INDEX_NAME_FILM)
    await elastic.load_documents(documents=films)

    url = urljoin(settings.movies_api_v1_url, 'films/')
    async with aiohttp_session.get(url, params=input) as response:
        status = response.status
        data = await response.json()

        assert status == expected['status']
        assert data[0]['imdb_rating'] == expected['rating']


@pytest.mark.parametrize(
    'input, expected',
    [
        (
            {
                'genre_uuid': 'e9c1dfa4-cfbf-40b8-b636-9075c2fd8429',
                'film_uuid': '721c9206-2e99-4247-aab2-d19463e4561c',
                'genre_search_uuid': 'e9c1dfa4-cfbf-40b8-b636-9075c2fd8429'
            },
            {'status': 200, 'length': 1, 'film_uuid': '721c9206-2e99-4247-aab2-d19463e4561c'}
        ),
        (
            {
                'genre_uuid': 'e9c1dfa4-cfbf-40b8-b636-9075c2fd8429',
                'film_uuid': '721c9206-2e99-4247-aab2-d19463e4561c',
                'genre_search_uuid': 'e9c1dfa4-cfbf-40b8-b636-9075c2fd8544'
            },
            {'status': 200, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_get_list_genre(
        create_elasticsearch_index,
        aiohttp_session,
        input: dict,
        expected: dict
):
    films = [
        Film(
            id=input['film_uuid'],
            title='The star. Episode 1',
            description='Description',
            rating=10,
            genres=[
                FilmGenre(
                    id=input['genre_uuid'],
                    name='Action'
                )
            ]
        ),
        Film(
            title='The star. Episode 2',
            description='Description',
            rating=1,
            genres=[
                FilmGenre(
                    name='Action'
                )
            ]
        )
    ]

    elastic = await create_elasticsearch_index(index_name=INDEX_NAME_FILM)
    await elastic.load_documents(documents=films)

    url = urljoin(settings.movies_api_v1_url, 'films/')
    async with aiohttp_session.get(url, params={'genre': input['genre_search_uuid']}) as response:
        status = response.status
        data = await response.json()

        assert status == expected['status']
        assert len(data) == expected['length']

        if 'film_uuid' in expected:
            assert data[0]['uuid'] == expected['film_uuid']


@pytest.mark.parametrize(
    "expected",
    [
        (
            {'uuid': str(uuid.uuid4())}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_get_by_id(
        create_elasticsearch_index,
        aiohttp_session,
        expected
):
    film = Film(
        id=expected['uuid'],
        title='The star',
        description='Description',
        rating=6.7
    )

    elastic = await create_elasticsearch_index(index_name=INDEX_NAME_FILM)
    await elastic.load_documents(documents=[film])

    url = f'{settings.movies_api_v1_url}films/{expected['uuid']}/'

    async with aiohttp_session.get(url) as response:
        data = await response.json()

        assert data['uuid'] == expected['uuid']


@pytest.mark.parametrize(
    "expected",
    [
        (
            {'uuid': str(uuid.uuid4())}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_get_by_id_from_redis(
        create_elasticsearch_index,
        aiohttp_session,
        expected
):
    film = Film(
        id=expected['uuid'],
        title='The star',
        description='Description',
        rating=6.7,
    )

    elastic = await create_elasticsearch_index(index_name=INDEX_NAME_FILM)
    await elastic.load_documents(documents=[film])

    url = f'{settings.movies_api_v1_url}films/{expected['uuid']}/'

    async with aiohttp_session.get(url) as response:
        data = await response.json()

        assert data['uuid'] == expected['uuid']

    await elastic.delete_index()

    async with aiohttp_session.get(url) as response:
        data = await response.json()

        assert data['uuid'] == expected['uuid']
