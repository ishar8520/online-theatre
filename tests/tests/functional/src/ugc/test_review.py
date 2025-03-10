from urllib.parse import urljoin

import pytest
from aiohttp.http import HTTPStatus
from dateutil import parser # type: ignore[import-untyped]

from ...settings import settings


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            {
                "user_id": "792c57e4-d8b8-40b7-8e5b-260f6db62a68",
                "film_id": "792c57e4-d8b8-40b7-8e5b-260f6db62333",
                "text": "Catch me if you can",
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
    url = urljoin(settings.ugc_api_v1_url, 'review/add')

    async with aiohttp_session.put(url, json=input_data) as response:
        status = response.status
        assert status == expected["status"]

        result_add = await response.json()

        assert "result" in result_add
        assert "id" in result_add["result"]
        assert result_add["result"]["user_id"] == input_data["user_id"]
        assert result_add["result"]["film_id"] == input_data["film_id"]
        assert result_add["result"]["text"] == input_data["text"]
        assert result_add["result"]["is_published"] is False
        assert result_add["result"]["published_at"] is None


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            {
                "user_id": "792c57e4-d8b8-40b7-8e5b-260f6db62a68",
                "film_id": "792c57e4-d8b8-40b7-8e5b-260f6db62333",
                "text": "Catch me if you can",
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
    url = urljoin(settings.ugc_api_v1_url, 'review/add')
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
                "text": "Catch me if you can",
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
    url = urljoin(settings.ugc_api_v1_url, 'review/add')
    async with aiohttp_session.put(url, json=input_data) as response_add:
        assert response_add.status == HTTPStatus.OK
        result_add = await response_add.json()

        assert "result" in result_add
        assert "id" in result_add["result"]

        url = urljoin(settings.ugc_api_v1_url, f'review/delete/{result_add["result"]["id"]}')
        async with aiohttp_session.delete(url, json=input_data) as response_del:
            assert response_del.status == expected["status"]

            result_del = await response_del.json()
            assert result_del["result"] is True


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            {
                "id": "67cdb68360862805fc1f6506"
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
    url = urljoin(settings.ugc_api_v1_url, f'review/delete/{input_data["id"]}')
    async with aiohttp_session.delete(url, json=input_data) as response_del:
        assert response_del.status == expected["status"]


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            {
                "user_id": "792c57e4-d8b8-40b7-8e5b-260f6db62a68",
                "film_id": "792c57e4-d8b8-40b7-8e5b-260f6db62333",
                "text": "Catch me if you can",
            },
            {
                "status": HTTPStatus.OK
            }
        ),
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_publish_review(
        aiohttp_session,
        clear_mongo,
        input_data,
        expected
) -> None:
    url = urljoin(settings.ugc_api_v1_url, 'review/add')
    async with aiohttp_session.put(url, json=input_data) as response_add:
        assert response_add.status == HTTPStatus.OK
        result_add = await response_add.json()

        assert "result" in result_add
        assert "id" in result_add["result"]
        assert result_add["result"]["user_id"] == input_data["user_id"]
        assert result_add["result"]["film_id"] == input_data["film_id"]
        assert result_add["result"]["text"] == input_data["text"]
        assert result_add["result"]["is_published"] is False

        url = urljoin(settings.ugc_api_v1_url, f'review/publish/{result_add["result"]["id"]}')
        async with aiohttp_session.post(url, json={"is_published": True}) as response_pub:
            assert response_pub.status == expected["status"]

            result_pub = await response_pub.json()

            assert "id" in result_pub["result"]
            assert result_pub["result"]["user_id"] == input_data["user_id"]
            assert result_pub["result"]["film_id"] == input_data["film_id"]
            assert result_pub["result"]["text"] == input_data["text"]
            assert result_pub["result"]["is_published"] is True

            try:
                published_at = parser.parse(result_pub["result"]["published_at"])
                assert published_at is not None
            except ValueError:
                assert False, f"is_published is not a valid date string. Given: {result_pub["result"]["published_at"]}"
