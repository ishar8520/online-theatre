from __future__ import annotations

import pytest
import uuid
from http import HTTPStatus
from urllib.parse import urljoin

from ...settings import settings

@pytest.mark.parametrize(
    'input, expected',
    [
        (
            {
                'name': 'admin',
                'permissions': ['create', 'read', 'update', 'delete']
            },
            {'status': HTTPStatus.CREATED}
        ),
        (
            {
                'name': 'admin',
                'permissions': ['create', 'read', 'update', 'delete']
            },
            {'status': HTTPStatus.BAD_REQUEST, 'detail': 'Duplicate role type'}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_add_role(aiohttp_session, input, expected):
    url = urljoin(settings.roles_api_v1_url, 'add/')
    async with aiohttp_session.post(url, json=input) as response:
        status = response.status
        assert status == expected['status']
        if expected['status'] == HTTPStatus.BAD_REQUEST:
            data = await response.json()
            assert data['detail'] == expected['detail']
