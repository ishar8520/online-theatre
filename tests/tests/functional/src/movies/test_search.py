import pytest
import uuid

from ...settings import settings
from urllib.parse import urljoin
from ...utils.elasticsearch.models.film import Film

INDEX_NAME_FILM = 'films'


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
