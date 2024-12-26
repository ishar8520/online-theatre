from __future__ import annotations

from urllib.parse import urljoin

import pytest

from ...settings import settings


@pytest.mark.asyncio(loop_scope='session')
async def test_openapi(aiohttp_session) -> None:
    openapi_url = urljoin(settings.movies_api_url, 'openapi.json')

    async with aiohttp_session.get(openapi_url) as response:
        assert response.status == 200
        response_data: dict = await response.json()

    assert set(response_data) == {
        'openapi',
        'info',
        'paths',
        'components',
    }
    assert response_data['info']['title'] == 'movies'
