from __future__ import annotations

import http
import pytest

from ....settings import settings


@pytest.mark.parametrize(
    "payload, expected",
    [
        (
            {
                "subject": "Broadcast",
                "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "notification_type": "push"
            },
            {'status': http.HTTPStatus.ACCEPTED}
        ),
        (
            {
                "subject": "Broadcast",
                "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            },
            {'status': http.HTTPStatus.ACCEPTED}
        ),
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_broadcast(aiohttp_session, payload, expected) -> None:

    url_broadcast = f"{settings.url_notification_api_messages}/broadcast"

    async with aiohttp_session.post(url_broadcast, json=payload) as response:
        assert response.status == expected["status"]
        response_data: dict = await response.json()

        assert response_data["result"] is True


@pytest.mark.parametrize(
    "user_id, payload, expected",
    [
        (
            "1a37a1ea-82e9-422f-b1cd-408e5598e333",
            {
                "subject": "Personalized",
                "template_id": "56a7a1ea-82e9-40c8-b1cd-408e5598e555",
                "notification_type": "push"
            },
            {'status': http.HTTPStatus.ACCEPTED}
        ),
        (
            "1a37a1ea-82e9-422f-b1cd-408e5598e333",
            {
                "subject": "Personalized",
                "template_id": "56a7a1ea-82e9-40c8-b1cd-408e5598e555",
            },
            {'status': http.HTTPStatus.ACCEPTED}
        ),
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_personalized(aiohttp_session, user_id, payload, expected) -> None:

    url_personalized = f"{settings.url_notification_api_messages}/personalized/{user_id}"

    async with aiohttp_session.post(url_personalized, json=payload) as response:
        assert response.status == expected["status"]
        response_data: dict = await response.json()

        assert response_data["result"] is True

