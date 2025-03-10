import uuid
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
    url = urljoin(settings.ugc_api_v1_url, 'bookmark/add')

    async with aiohttp_session.put(url, json=input_data) as response:
        status = response.status
        assert status == expected["status"]

        result_add = await response.json()

        assert "result" in result_add
        assert "id" in result_add["result"]
        assert result_add["result"]["user_id"] == input_data["user_id"]
        assert result_add["result"]["film_id"] == input_data["film_id"]


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            {
                "user_id": "792c57e4-d8b8-40b7-8e5b-260f6db62a68",
                "film_id": "792c57e4-d8b8-40b7-8e5b-260f6db62333",
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
    url = urljoin(settings.ugc_api_v1_url, 'bookmark/add')
    await aiohttp_session.put(url, json=input_data)

    async with aiohttp_session.put(url, json=input_data) as response:
        status = response.status
        assert status == expected["status"]


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            {
                "user_id": "792c57e4-d8b8-40b7-8e5b-260f6db62a68",
                "film_id": "792c57e4-d8b8-40b7-8e5b-260f6db62333",
            },
            {
                "status": HTTPStatus.OK
            }
        ),
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_delete(
        aiohttp_session,
        clear_mongo,
        input_data,
        expected
) -> None:
    url = urljoin(settings.ugc_api_v1_url, 'bookmark/add')
    async with aiohttp_session.put(url, json=input_data) as response_add:
        assert response_add.status == HTTPStatus.OK
        result_add = await response_add.json()

        assert "result" in result_add
        assert "id" in result_add["result"]

        url = urljoin(settings.ugc_api_v1_url, f'bookmark/delete/{result_add["result"]["id"]}')
        async with aiohttp_session.delete(url, json=input_data) as response_del:
            assert response_del.status == expected["status"]

            result_del = await response_del.json()
            assert result_del["result"] is True


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            {
                "id": "47cdb67854012805fc1f6587"
            },
            {
                "status": HTTPStatus.NOT_FOUND
            }
        ),
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_delete_by_unknown_id(
        aiohttp_session,
        clear_mongo,
        input_data,
        expected
) -> None:
    url = urljoin(settings.ugc_api_v1_url, f'bookmark/delete/{input_data["id"]}')
    async with aiohttp_session.delete(url, json=input_data) as response_del:
        assert response_del.status == expected["status"]


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            {
                "user_id": uuid.uuid4(),
                "count": 5,
            },
            {
                "status": HTTPStatus.OK,
                "count": 5,
            }
        ),
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_get_list(
        aiohttp_session,
        clear_mongo,
        input_data,
        expected
) -> None:
    url = urljoin(settings.ugc_api_v1_url, 'bookmark/add')

    for i in range(0, input_data["count"]):
        bookmark = {
            "user_id": str(input_data["user_id"]),
            "film_id": str(uuid.uuid4()),
        }
        await aiohttp_session.put(url, json=bookmark)

    url = urljoin(settings.ugc_api_v1_url, f'bookmark/get_list/{input_data["user_id"]}')
    async with aiohttp_session.get(url) as response:
        status = response.status
        assert status == expected["status"]

        result_get = await response.json()

        assert "result" in result_get
        assert len(result_get["result"]) == expected["count"]
