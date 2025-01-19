from __future__ import annotations

from urllib.parse import urljoin

import pytest
import http

from ...settings import settings


@pytest.mark.parametrize(
    "input_data, expected_data",
    [
        (
            {
                'login': 'test_user',
                'password': '123456',
            },
            {
                'count_login': 1,
            }
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_get_login_history(
        aiohttp_session,
        clean_all_tables_before,
        input_data,
        expected_data
):
    user_create_data = {
        'login': input_data['login'],
        'password': input_data['password']
    }
    url = urljoin(settings.auth_api_v1_url, 'register')
    async with aiohttp_session.post(url, json=user_create_data) as register_response:
        assert register_response.status == http.HTTPStatus.CREATED

    user_login_data = {
        'grant_type': 'password',
        'username': user_create_data['login'],
        'password': user_create_data['password'],
        'scope': '',
        'client_id': 'string',
        'client_secret': 'secret'
    }
    url = urljoin(settings.auth_api_v1_url, 'jwt/login')
    async with aiohttp_session.post(url, data=user_login_data) as login_response:
        assert login_response.status ==  http.HTTPStatus.OK

        data = await login_response.json()
        token_jwt = data['access_token']
        token_type = data['token_type']
        headers = {
            'Accept': 'application/json',
            'Authorization': f'{token_type.title()} {token_jwt}'
        }

        url = urljoin(settings.auth_api_v1_url, 'users/get_login_history')
        async with aiohttp_session.get(url, headers=headers) as history_response:
            status = history_response.status
            assert status == http.HTTPStatus.OK
            data = await history_response.json()
            assert len(data) == expected_data['count_login']
