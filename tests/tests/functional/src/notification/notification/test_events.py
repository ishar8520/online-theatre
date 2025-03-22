from __future__ import annotations

import http
import pytest

from ....settings import settings


@pytest.mark.parametrize(
    "payload, expected",
    [
        (
            {
                "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "notification_type": "push"
            },
            {'status': http.HTTPStatus.ACCEPTED}
        ),
        (
            {
                "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            },
            {'status': http.HTTPStatus.ACCEPTED}
        ),
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_registration(aiohttp_session, payload, expected) -> None:

    url_registration = f"{settings.url_notification_api_events}/registration"

    async with aiohttp_session.post(url_registration, json=payload) as response:
        assert response.status == expected["status"]
        response_data: dict = await response.json()

        assert response_data["result"] is True


@pytest.mark.parametrize(
    "payload, expected",
    [
        (
            {
                "film_id": "56a7a1ea-82e9-40c8-b1cd-408e5598e555",
                "notification_type": "push"
            },
            {'status': http.HTTPStatus.ACCEPTED}
        ),
        (
            {
                "film_id": "56a7a1ea-82e9-40c8-b1cd-408e5598e555",
            },
            {'status': http.HTTPStatus.ACCEPTED}
        ),
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_new_movie(aiohttp_session, payload, expected) -> None:

    url_registration = f"{settings.url_notification_api_events}/new_movie"

    async with aiohttp_session.post(url_registration, json=payload) as response:
        assert response.status == expected["status"]
        response_data: dict = await response.json()

        assert response_data["result"] is True

