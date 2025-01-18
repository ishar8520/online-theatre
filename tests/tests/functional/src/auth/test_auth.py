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
                'grand_type': 'password',
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


@pytest.mark.parametrize(
    'input',
    [
        (
            {}
        ),
        (
            {
                'grand_type': 'password',
                'username': 'testuser',
                'password': 'strongpassword',
                'scope': '',
                'client_id': 'string',
                'client_secret': 'secret'
            }
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_logout(aiohttp_session, input):
    if input:
        url = urljoin(settings.auth_api_v1_url, 'jwt/login/')
        async with aiohttp_session.post(url, data=input) as response:
            status = response.status
            assert status ==  http.HTTPStatus.OK
            data = await response.json()
            token_jwt = data['access_token']
            token_type = data['token_type']
            headers = {
                'accept': 'application/json',
                'Authorization': f'{token_type.title()} {token_jwt}'
            }
        url = urljoin(settings.auth_api_v1_url, 'jwt/logout/')
        async with aiohttp_session.post(url, headers=headers, data='') as response:
            status = response.status
            assert status == http.HTTPStatus.NO_CONTENT
    else:
        url = urljoin(settings.auth_api_v1_url, 'jwt/logout/')
        async with aiohttp_session.post(url, headers='', data='') as response:
            status = response.status
            assert status == http.HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio(loop_scope='session')
async def test_get_current_user(aiohttp_session):
    input = {
                'grand_type': 'password',
                'username': 'testuser',
                'password': 'strongpassword',
                'scope': '',
                'client_id': 'string',
                'client_secret': 'secret'
            }
    url = urljoin(settings.auth_api_v1_url, 'jwt/login/')
    async with aiohttp_session.post(url, data=input) as response:
        status = response.status
        assert status ==  http.HTTPStatus.OK
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
        assert data['login'] == input['username']


@pytest.mark.parametrize(
    'input, patch',
    [
        (
            {
                'grand_type': 'password',
                'username': 'testuser',
                'password': 'strongpassword',
                'scope': '',
                'client_id': 'string',
                'client_secret': 'secret'
            },
            {
                'login': 'testuser2',
                'password': 'strongpassword2',
                'is_superuser': False
            }
        ),
        (
            {
                'grand_type': 'password',
                'username': 'testuser',
                'password': 'strongpassword',
                'scope': '',
                'client_id': 'string',
                'client_secret': 'secret'
            },
            {
                'login': 'testuser2',
                'password': 'strongpassword2',
                'is_superuser': False
            }
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_patch_current_user(aiohttp_session, input, patch):
    input = {
                'grand_type': 'password',
                'username': 'testuser',
                'password': 'strongpassword',
                'scope': '',
                'client_id': 'string',
                'client_secret': 'secret'
            }
    url = urljoin(settings.auth_api_v1_url, 'jwt/login/')
    async with aiohttp_session.post(url, data=input) as response:
        status = response.status
        assert status ==  http.HTTPStatus.OK
        data = await response.json()
        token_jwt = data['access_token']
        token_type = data['token_type']
        headers = {
            'accept': 'application/json',
            'Authorization': f'{token_type.title()} {token_jwt}'
        }
    input = {
        'login': 'testuser2',
        'password': 'strongpassword2',
        'is_superuser': False
    }
    url = urljoin(settings.auth_api_v1_url, 'users/me/')
    async with aiohttp_session.patch(url, headers=headers, data=input) as response:
        status = response.status
        assert status == http.HTTPStatus.OK
        data = await response.json()
        assert data['login'] == input['login']
