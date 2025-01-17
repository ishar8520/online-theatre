from __future__ import annotations

import pytest
from urllib.parse import urljoin
import http

from ...settings import settings


@pytest.mark.parametrize(
    'input, expected',
    [
        (
            {
                'login': 'testuser',
                'password': 'strongpassword',
                'is_superuser': False
            },
            {'status': http.HTTPStatus.CREATED}
        ),
        (
            {
                'login': 'testuser',
                'password': 'strongpassword',
                'is_superuser': False
            },
            {'status': http.HTTPStatus.BAD_REQUEST, 'detail': 'REGISTER_USER_ALREADY_EXISTS'}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_register(aiohttp_session, input, expected):
    url = urljoin(settings.auth_api_v1_url, 'register/')
    async with aiohttp_session.post(url, json=input) as response:
        status = response.status
        print(response)
        
        assert status == expected['status']
        data = await response.json()
        if expected['status'] == http.HTTPStatus.BAD_REQUEST:
            assert data['detail'] == expected['detail']


@pytest.mark.asyncio(loop_scope='session')
async def test_login(aiohttp_session):
    login = {
                'grand_type': 'password',
                'username': 'test_user',
                'password': 'password',
                'scope': '',
                'client_id': 'string',
                'client_secret': 'secret'
            }
    url = urljoin(settings.auth_api_v1_url, 'jwt/login/')
    async with aiohttp_session.post(url, json=login) as response:
        status = response.status
        assert status == http.HTTPStatus.OK

@pytest.mark.parametrize(
    'input, expected',
    [
        (
            {},
            {'status': http.HTTPStatus.UNAUTHORIZED}
        ),
        (
            {
                'login': 'testuser',
                'password': 'strongpassword',
                'is_superuser': 'false'
            },
            {'status': http.HTTPStatus.OK}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_logout(aiohttp_session, input, expected):
    if input:
        url = urljoin(settings.auth_api_v1_url, 'jwt/login/')
        async with aiohttp_session.post(url, data=input) as response:
            status = response.status
            assert status == http.HTTPStatus.OK
    url = urljoin(settings.auth_api_v1_url, 'jwt/logout/')
    async with aiohttp_session.post(url) as response:
        status = response.status
        assert status == expected['status']


@pytest.mark.asyncio(loop_scope='session')
async def test_get_user(aiohttp_session):
    url = urljoin(settings.auth_api_v1_url, 'users/me/')
    async with aiohttp_session.post(url) as response:
        status = response.status
        assert status == http.HTTPStatus.OK
