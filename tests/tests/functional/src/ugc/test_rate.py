from urllib.parse import urljoin

import pytest
from aiohttp.http import HTTPStatus

from ...settings import settings


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            {
                "user_id": "792c57e4-d8b8-40b7-8e5b-260f6db62a68",
                "film_id": "792c57e4-d8b8-40b7-8e5b-260f6db62333",
                "rate": 5
            },
            {
                "status": HTTPStatus.OK
            }
        ),
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_add(
        aiohttp_session,
        clear_mongo,
        input_data,
        expected
) -> None:
    url = urljoin(settings.ugc_api_v1_url, 'rate/add')

    async with aiohttp_session.put(url, json=input_data) as response:
        status = response.status
        assert status == expected["status"]

        response = await response.json()
        assert "id" in response


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            {
                "user_id": "792c57e4-d8b8-40b7-8e5b-260f6db62a68",
                "film_id": "792c57e4-d8b8-40b7-8e5b-260f6db62333",
                "rate": 5
            },
            {
                "status": HTTPStatus.BAD_REQUEST
            }
        ),
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_add_duplicate(
        aiohttp_session,
        clear_mongo,
        input_data,
        expected
) -> None:
    url = urljoin(settings.ugc_api_v1_url, 'rate/add')
    await aiohttp_session.put(url, json=input_data)

    async with aiohttp_session.put(url, json=input_data) as response:
        status = response.status
        assert status == expected["status"]
