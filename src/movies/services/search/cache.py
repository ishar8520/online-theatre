from __future__ import annotations

import hashlib
import json
from typing import Any

from ..cache import AbstractCache


class SearchCache:
    cache: AbstractCache

    def __init__(self, *, cache: AbstractCache) -> None:
        self.cache = cache

    async def get(self, *, index: str, command: str, params: dict) -> Any | None:
        cache_key = self._create_cache_key(index=index, command=command, params=params)
        value_json: str | None = await self.cache.get(cache_key)

        if value_json is None:
            return None

        return json.loads(value_json)

    async def set(self, *, index: str, command: str, params: dict, value: Any) -> None:
        cache_key = self._create_cache_key(index=index, command=command, params=params)
        value_json = json.dumps(value)

        await self.cache.set(cache_key, value_json)

    def _create_cache_key(self, *, index: str, command: str, params: dict) -> str:
        key_dict = {
            'index': index,
            'command': command,
            'params': params,
        }
        key_json = json.dumps(key_dict, sort_keys=True)
        key_hash = hashlib.sha256(key_json.encode()).hexdigest()

        return f'{index}-{command}-{key_hash}'
