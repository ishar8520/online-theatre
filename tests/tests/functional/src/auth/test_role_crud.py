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


@pytest.mark.parametrize(
    "input_data, expected_status, expected_detail",
    [
        (
            {"name": "subscribers_updated", "code": "subscribers"}, 
            HTTPStatus.OK, 
            None
        ),
        (
            {"name": "subscribers_updated", "code": "subscribers"}, 
            HTTPStatus.BAD_REQUEST, 
            "Duplicate role type"
        ),
        (
            {"name": "subscribers_updated12", "code": "subscribers"}, 
            HTTPStatus.NOT_FOUND, 
            "Role not found"
        ),
    ],
)

@pytest.mark.asyncio(loop_scope="session")
async def test_update_role(aiohttp_session, create_role, input_data, expected_status, expected_detail):
    role_id = create_role.id
    url = urljoin(settings.auth_api_v1_url, f"roles/update/{role_id}/")
    async with aiohttp_session.put(url, json=input_data) as response:
        status = response.status
        assert status == expected_status
        if expected_status == HTTPStatus.BAD_REQUEST or expected_status == HTTPStatus.NOT_FOUND:
            data = await response.json()
            assert data["detail"] == expected_detail
        elif expected_status == HTTPStatus.OK:
            data = await response.json()
            assert "id" in data
            assert data["name"] == input_data["name"]
            assert data["code"] == input_data["code"]
