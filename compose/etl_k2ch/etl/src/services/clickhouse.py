from __future__ import annotations

from typing import Any
from clickhouse_driver import Client

from ..core.config import settings


class ClickhouseService:
    _client: Client

    def __init__(self, ):
        self._client = Client(host=settings.clickhouse.host)

    def insert(self, table_name: str, data: dict[str, Any]):
        keys_string = ', '.join(data.keys())
        values_list = list(data.values())

        return self._client.execute(
            f'INSERT INTO ugc.{table_name} ({keys_string}) VALUES',
            [values_list]
        )
