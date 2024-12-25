import pytest
import uuid

from ...settings import settings
from urllib.parse import urljoin
from ...utils.elasticsearch.models.film import Film
from ...utils.elasticsearch.models.person import Person

INDEX_NAME_FILM = 'films'
INDEX_NAME_PERSON = 'persons'


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            {'search': 'Star'},
            {'status': 200, 'length': 1}
        ),
        (
            {'search': 'Mashed potato'},
            {'status': 200, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_search_film(
        create_elasticsearch_index,
        aiohttp_session,
        clear_redis_cache,
        input,
        expected
):
    film = Film(
        id=str(uuid.uuid4()),
        title='The Star',
        description='Description',
        rating=6.7,
    )

    await clear_redis_cache()
    elastic = await create_elasticsearch_index(index_name=INDEX_NAME_FILM)
    await elastic.load_data(documents=[film.model_dump()])

    url = urljoin(settings.movies_api_v1_url, 'films/search/')
    async with aiohttp_session.get(url, params={'query': input['search']}) as response:
        status = response.status
        data = await response.json()

        assert status == expected['status']
        assert len(data) == expected['length']


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            {
                'person_uuid': 'e9c1dfa4-cfbf-40b8-b636-9075c2fd8429',
                'person_full_name': 'Jeffry Jones',
                'search_full_name': 'jones'
            },
            {'status': 200, 'length': 1, 'person_uuid': 'e9c1dfa4-cfbf-40b8-b636-9075c2fd8429'}
        ),
        (
            {
                'person_uuid': 'e9c1dfa4-cfbf-40b8-b636-9075c2fd8429',
                'person_full_name': 'Jeffry Jones',
                'search_full_name': 'Julie Pi'
            },
            {'status': 200, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_search_person(
        create_elasticsearch_index,
        aiohttp_session,
        clear_redis_cache,
        input,
        expected
):
    persons = [
        Person(
            id=input['person_uuid'],
            full_name=input['person_full_name']
        ).model_dump(),
        Person(
            id=str(uuid.uuid4()),
            full_name='Josse Sue'
        ).model_dump(),
    ]

    await clear_redis_cache()
    elastic = await create_elasticsearch_index(index_name=INDEX_NAME_PERSON)
    await elastic.load_data(documents=persons)

    url = urljoin(settings.movies_api_v1_url, 'persons/search/')
    async with aiohttp_session.get(url, params={'query': input['search_full_name']}) as response:
        status = response.status
        data = await response.json()

        assert status == expected['status']
        assert len(data) == expected['length']

        if 'person_uuid' in expected:
            assert data[0]['uuid'] == expected['person_uuid']


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            {
                'person_uuid': 'e9c1dfa4-cfbf-40b8-b636-9075c2fd8429',
                'person_full_name': 'Jeffry Jones',
                'search_full_name': 'jones'
            },
            {'status': 200, 'length': 1, 'person_uuid': 'e9c1dfa4-cfbf-40b8-b636-9075c2fd8429'}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_search_person_with_redis(
        create_elasticsearch_index,
        aiohttp_session,
        clear_redis_cache,
        input,
        expected
):
    person = Person(
        id=input['person_uuid'],
        full_name=input['person_full_name']
    )

    await clear_redis_cache()
    elastic = await create_elasticsearch_index(index_name=INDEX_NAME_PERSON)
    await elastic.load_data(documents=[person.model_dump()])

    async def inner_test_search_person_with_redis(aiohttp_session, input, expected):
        url = urljoin(settings.movies_api_v1_url, 'persons/search/')
        async with aiohttp_session.get(url, params={'query': input['search_full_name']}) as response:
            status = response.status
            data = await response.json()

            assert status == expected['status']
            assert len(data) == expected['length']

            if 'person_uuid' in expected:
                assert data[0]['uuid'] == expected['person_uuid']

    await inner_test_search_person_with_redis(aiohttp_session, input, expected)

    await elastic.delete_index()

    await inner_test_search_person_with_redis(aiohttp_session, input, expected)
