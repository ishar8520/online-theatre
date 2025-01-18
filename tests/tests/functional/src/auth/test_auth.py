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
        assert status == expected['status']
        data = await response.json()
        if expected['status'] == http.HTTPStatus.BAD_REQUEST:
            assert data['detail'] == expected['detail']

@pytest.mark.parametrize(
    'input, expected',
    [
        (
            {
                'grand_type': 'strongpassword',
                'username': 'testuser',
                'password': 'strongpassword',
                'scope': '',
                'client_id': 'string',
                'client_secret': 'secret'
            },
            {'status': http.HTTPStatus.OK}
        ),
        (
            {
                'grand_type': 'password',
                'username': 'test_user',
                'password': 'password',
                'scope': '',
                'client_id': 'string',
                'client_secret': 'secret'
            },
            {'status': http.HTTPStatus.BAD_REQUEST, 'detail': 'LOGIN_BAD_CREDENTIALS'}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_login(aiohttp_session, input, expected):
    url = urljoin(settings.auth_api_v1_url, 'jwt/login/')
    async with aiohttp_session.post(url, data=input) as response:
        status = response.status
        assert status == expected['status']
        data = await response.json()
        if expected['status'] == http.HTTPStatus.BAD_REQUEST:
            assert data['detail'] == expected['detail']
        # else:
        #     print(data)

@pytest.mark.parametrize(
    'num, input, expected',
    [
        (
            1,
            {},
            {'status': http.HTTPStatus.UNAUTHORIZED}
        ),
        (
            2,
            {
                'grand_type': 'strongpassword',
                'username': 'testuser',
                'password': 'strongpassword',
                'scope': '',
                'client_id': 'string',
                'client_secret': 'secret'
            },
            {'status': http.HTTPStatus.OK}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_logout(aiohttp_session, num, input, expected):
    if num == 1:
        url = urljoin(settings.auth_api_v1_url, 'users/me/')
        async with aiohttp_session.get(url) as response:
            status = response.status
            assert status == http.HTTPStatus.UNAUTHORIZED
        
        url = urljoin(settings.auth_api_v1_url, 'jwt/logout/')
        async with aiohttp_session.post(url) as response:
            status = response.status
            assert status == http.HTTPStatus.UNAUTHORIZED
            
    elif num == 2:
        url = urljoin(settings.auth_api_v1_url, 'users/me/')
        async with aiohttp_session.get(url) as response:
            status = response.status
            assert status == http.HTTPStatus.UNAUTHORIZED
        
        url = urljoin(settings.auth_api_v1_url, 'jwt/login/')
        async with aiohttp_session.post(url, data=input) as response:
            status = response.status
            assert status == http.HTTPStatus.OK
            data = await response.json()
            print(data)
            
        url = urljoin(settings.auth_api_v1_url, 'users/me/')
        async with aiohttp_session.get(url) as response:
            status = response.status
            assert status == http.HTTPStatus.OK
            
        url = urljoin(settings.auth_api_v1_url, 'jwt/logout/')
        async with aiohttp_session.post(url) as response:
            status = response.status
            assert status == http.HTTPStatus.OK

        url = urljoin(settings.auth_api_v1_url, 'users/me/')
        async with aiohttp_session.get(url) as response:
            status = response.status
            assert status == http.HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio(loop_scope='session')
async def test_get_current_user(aiohttp_session):
    url = urljoin(settings.auth_api_v1_url, 'users/me/')
    async with aiohttp_session.get(url) as response:
        status = response.status
        assert status == http.HTTPStatus.OK
