from __future__ import annotations

import pytest
from urllib.parse import urljoin
import http

from ...settings import settings

@pytest.mark.parametrize(
    "input, expected",
    [
        (
            {
                'login': 'testuser',
                'password': 'strongpassword',
                'is_superuser': 'False'
            },
            {'status': http.HTTPStatus.NOT_FOUND}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_register(aiohttp_session, input, expected):
    """Test register user"""
    url = urljoin(settings.auth_api_url, 'register/')
    async with aiohttp_session.post(url, params=input) as response:
        status = response.status
        data = await response.json()
        assert status == expected['status']

@pytest.mark.parametrize(
    "input, expected",
    [
        (
            {
                'login': 'testuser',
                'password': 'strongpassword',
                'is_superuser': 'False'
            },
            {'status': http.HTTPStatus.NOT_FOUND}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_login(aiohttp_session, input, expected):
    """Test user login"""
    url = urljoin(settings.auth_api_url, 'login/')
    async with aiohttp_session.post(url, params=input) as response:
        status = response.status
        data = await response.json()
        assert status == expected['status']

@pytest.mark.parametrize(
    "input, expected",
    [
        (
            {
                'login': 'testuser',
                'password': 'strongpassword',
                'is_superuser': 'False'
            },
            {'status': http.HTTPStatus.NOT_FOUND}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_logout(aiohttp_session, input, expected):
    """Test user logout"""
    url = urljoin(settings.auth_api_url, 'logout/')
    async with aiohttp_session.post(url, params=input) as response:
        status = response.status
        data = await response.json()
        assert status == expected['status']