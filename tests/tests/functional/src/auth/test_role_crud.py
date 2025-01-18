from __future__ import annotations

from http import HTTPStatus
from urllib.parse import urljoin

import pytest

from ...settings import settings


@pytest.mark.parametrize(
    "input_data, expected_status, expected_detail",
    [
        (
            {"name": "admin", "code": "admin"}, HTTPStatus.CREATED, None),
        (
            {"name": "admin", "code": "admin"},
            HTTPStatus.BAD_REQUEST,
            "Duplicate role type",
        ),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_add_role(aiohttp_session, input_data, expected_status, expected_detail):
    url = urljoin(settings.auth_api_v1_url, "roles/add/")
    async with aiohttp_session.post(url, json=input_data) as response:
        status = response.status
        assert status == expected_status
        if expected_status == HTTPStatus.BAD_REQUEST:
            data = await response.json()
            assert data["detail"] == expected_detail
        elif expected_status == HTTPStatus.CREATED:
            data = await response.json()
            assert "id" in data
            assert data["name"] == input_data["name"]
            assert data["code"] == input_data["code"]
