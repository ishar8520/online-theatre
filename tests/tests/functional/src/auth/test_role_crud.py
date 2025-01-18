from __future__ import annotations

import uuid
from http import HTTPStatus
from urllib.parse import urljoin

import pytest

from ...settings import settings

role_id_save = {}


@pytest.mark.parametrize(
    "input_data, expected_status, expected_detail",
    [
        ({"name": "admin", "code": "admin"}, HTTPStatus.CREATED, None),
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
            role_id_save["id"] = data["id"]


@pytest.mark.parametrize(
    "input_data, expected_status, expected_detail",
    [
        ({"name": "admin_updated", "code": "admin"}, HTTPStatus.OK, None),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_update_role(
    aiohttp_session, input_data, expected_status, expected_detail
):
    role_id = role_id_save.get("id")
    url = urljoin(settings.auth_api_v1_url, f"roles/update/{role_id}/")
    async with aiohttp_session.put(url, json=input_data) as response:
        status = response.status
        assert status == expected_status
        if (
            expected_status == HTTPStatus.BAD_REQUEST
            or expected_status == HTTPStatus.NOT_FOUND
        ):
            data = await response.json()
            assert data["detail"] == expected_detail
        elif expected_status == HTTPStatus.OK:
            data = await response.json()
            assert "id" in data
            assert data["name"] == input_data["name"]
            assert data["code"] == input_data["code"]


@pytest.mark.parametrize(
    "input_data, expected_status, expected_detail",
    [
        (
            {"name": "admin_updated_duplicate", "code": "admin"},
            HTTPStatus.BAD_REQUEST,
            "Duplicate role type",
        )
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_update_role_duplicate(
    aiohttp_session, create_role, input_data, expected_status, expected_detail
):
    role_id = create_role.id
    url = urljoin(settings.auth_api_v1_url, f"roles/update/{role_id}/")
    async with aiohttp_session.put(url, json=input_data) as response:
        status = response.status
        assert status == expected_status
        if (
            expected_status == HTTPStatus.BAD_REQUEST
            or expected_status == HTTPStatus.NOT_FOUND
        ):
            data = await response.json()
            assert data["detail"] == expected_detail


@pytest.mark.parametrize(
    "input_data, expected_status, expected_detail",
    [
        (
            {"name": "subscribers123", "code": "users"},
            HTTPStatus.NOT_FOUND,
            "Role not found",
        ),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_update_role_not_found(
    aiohttp_session, input_data, expected_status, expected_detail
):
    role_id = str(uuid.uuid4())
    url = urljoin(settings.auth_api_v1_url, f"roles/update/{role_id}/")
    async with aiohttp_session.put(url, json=input_data) as response:
        status = response.status
        assert status == expected_status
        if expected_status == HTTPStatus.NOT_FOUND:
            data = await response.json()
            assert data["detail"] == expected_detail


@pytest.mark.parametrize(
    "expected_result, " "expected_status",
    [
        (
            {"name": "admin_updated", "code": "admin"},
            HTTPStatus.OK,
        ),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_get_role(aiohttp_session, expected_result, expected_status):
    role_id = role_id_save.get("id")
    url = urljoin(settings.auth_api_v1_url, f"roles/get/{role_id}/")
    async with aiohttp_session.get(url) as response:
        status = response.status
        data = await response.json()
        assert status == expected_status
        if expected_status == HTTPStatus.OK:
            data = await response.json()
            assert expected_result["name"] == data["name"]
            assert expected_result["code"] == data["code"]
            assert len(data["created"]) > 2
            assert len(data["modified"]) > 2


@pytest.mark.parametrize(
    "expected_status",
    [
        HTTPStatus.OK,
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_get_many_roles(aiohttp_session, expected_status):
    url = urljoin(settings.auth_api_v1_url, f"roles/list/")
    async with aiohttp_session.get(url) as response:
        status = response.status
        data = await response.json()
        assert status == expected_status
        if expected_status == HTTPStatus.OK:
            data = await response.json()
            assert isinstance(data, list)
            assert len(data) == 2


@pytest.mark.parametrize(
    "expected_status",
    [
        HTTPStatus.OK,
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_delete_role(aiohttp_session, create_role, expected_status):
    role_id = create_role.id
    url = urljoin(settings.auth_api_v1_url, f"roles/delete/{role_id}/")
    async with aiohttp_session.delete(url) as response:
        status = response.status
        data = await response.json()
        assert status == expected_status
        if expected_status == HTTPStatus.OK:
            data = await response.json()
            assert "id" in data
