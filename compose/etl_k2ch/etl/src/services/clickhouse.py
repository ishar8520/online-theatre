from __future__ import annotations

from typing import Any
from clickhouse_driver import Client

from ..core.config import settings


class ClickhouseService:
    _client: Client

    def __init__(self, ):
        self._client = Client(host=settings.clickhouse.host)

    def insert(self, table_name: str, table_columns: list, values: list):
        keys_string = ', '.join(table_columns)

        return self._client.execute(
            f'INSERT INTO ugc.{table_name} ({keys_string}) VALUES',
            values
        )
