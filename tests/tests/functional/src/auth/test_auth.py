from __future__ import annotations

import http
from urllib.parse import urljoin

import pytest

from ...settings import settings


@pytest.mark.asyncio(loop_scope='session')
async def test_register(aiohttp_session, clean_all_tables_before) -> None:
    login_data = {
        'login': 'test_user',
        'password': 'password',
    }
    url = urljoin(settings.auth_api_v1_url, 'register/')

    async with aiohttp_session.post(url, json=login_data) as response:
        status = response.status
        assert status == http.HTTPStatus.CREATED


@pytest.mark.asyncio(loop_scope='session')
async def test_register_exists_user(aiohttp_session) -> None:
    login_data = {
        'login': 'test_user',
        'password': 'password',
    }
    url = urljoin(settings.auth_api_v1_url, 'register/')

    await aiohttp_session.post(url, json=login_data)
    async with aiohttp_session.post(url, json=login_data) as response:
        status = response.status
        data = await response.json()

    assert status == http.HTTPStatus.BAD_REQUEST
    assert data['detail'] == 'REGISTER_USER_ALREADY_EXISTS'


@pytest.mark.parametrize(
    'input_data, expected_data',
    [
        (
                {
                    'grant_type': 'password',
                    'username': 'test_user',
                    'password': 'password',
                },
                {'status': http.HTTPStatus.OK},
        ),
        (
                {
                    'grant_type': 'password',
                    'username': 'test_user_BAD_CREDENTIALS',
                    'password': 'password',
                },
                {'status': http.HTTPStatus.BAD_REQUEST, 'detail': 'LOGIN_BAD_CREDENTIALS'},
        ),
    ],
)
@pytest.mark.asyncio(loop_scope='session')
async def test_login(aiohttp_session, input_data, expected_data) -> None:
    login_data = {
        'login': 'test_user',
        'password': 'password',
    }

    url = urljoin(settings.auth_api_v1_url, 'register/')
    await aiohttp_session.post(url, json=login_data)

    url = urljoin(settings.auth_api_v1_url, 'jwt/login/')
    async with aiohttp_session.post(url, data=input_data) as response:
        status = response.status
        assert status == expected_data['status']

        data = await response.json()
        if expected_data['status'] == http.HTTPStatus.BAD_REQUEST:
            assert data['detail'] == expected_data['detail']


@pytest.mark.asyncio(loop_scope='session')
async def test_get_current_user(aiohttp_session) -> None:
    login_data = {
        'grant_type': 'password',
        'username': 'test_user',
        'password': 'password',
    }
    url = urljoin(settings.auth_api_v1_url, 'jwt/login/')

    async with aiohttp_session.post(url, data=login_data) as response:
        status = response.status
        assert status == http.HTTPStatus.OK
        data = await response.json()

    token_jwt = data['access_token']
    token_type = data['token_type']
    headers = {
        'accept': 'application/json',
        'Authorization': f'{token_type.title()} {token_jwt}'
    }
    url = urljoin(settings.auth_api_v1_url, 'users/me/')

    async with aiohttp_session.get(url, headers=headers) as response:
        status = response.status
        assert status == http.HTTPStatus.OK
        data = await response.json()
        assert data['login'] == login_data['username']


@pytest.mark.asyncio(loop_scope='session')
async def test_patch_current_user(aiohttp_session, clean_all_tables_after) -> None:
    login_data = {
        'grant_type': 'password',
        'username': 'test_user',
        'password': 'password',
    }
    patch_data = {
        'login': 'test_user2',
        'password': 'password',
        'is_superuser': False,
    }
    url = urljoin(settings.auth_api_v1_url, 'jwt/login/')

    async with aiohttp_session.post(url, data=login_data) as response:
        status = response.status
        assert status == http.HTTPStatus.OK
        data = await response.json()

    token_jwt = data['access_token']
    token_type = data['token_type']
    headers = {
        'accept': 'application/json',
        'Authorization': f'{token_type.title()} {token_jwt}',
        'Content-Type': 'application/json',
    }
    url = urljoin(settings.auth_api_v1_url, 'users/me/')

    async with aiohttp_session.get(url, headers=headers) as response:
        status = response.status
        assert status == http.HTTPStatus.OK

    url = urljoin(settings.auth_api_v1_url, 'users/me/')

    async with aiohttp_session.patch(url, headers=headers, json=patch_data) as response:
        status = response.status
        assert status == http.HTTPStatus.OK
        data = await response.json()
        assert data['login'] == patch_data['login']


@pytest.mark.asyncio(loop_scope='session')
async def test_logout(aiohttp_session) -> None:
    login_data = {
        'grant_type': 'password',
        'username': 'test_user2',
        'password': 'password',
    }
    url = urljoin(settings.auth_api_v1_url, 'jwt/login/')

    async with aiohttp_session.post(url, data=login_data) as response:
        status = response.status
        assert status == http.HTTPStatus.OK
        data = await response.json()

    token_jwt = data['access_token']
    token_type = data['token_type']
    headers = {
        'accept': 'application/json',
        'Authorization': f'{token_type.title()} {token_jwt}',
    }
    url = urljoin(settings.auth_api_v1_url, 'jwt/logout/')

    async with aiohttp_session.post(url, headers=headers) as response:
        status = response.status
        assert status == http.HTTPStatus.NO_CONTENT

    async with aiohttp_session.post(url, headers=headers) as response:
        status = response.status
        assert status == http.HTTPStatus.UNAUTHORIZED
