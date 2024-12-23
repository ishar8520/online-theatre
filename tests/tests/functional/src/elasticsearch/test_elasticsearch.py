from __future__ import annotations

import pytest


@pytest.mark.asyncio(loop_scope='session')
async def test_elasticsearch_indices(create_elasticsearch_index) -> None:
    for index_name in [
        'films',
        'genres',
        'persons',
    ]:
        await create_elasticsearch_index(index_name=index_name)
