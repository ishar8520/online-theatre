from __future__ import annotations

from collections import defaultdict
from time import time
from clickhouse_driver import Client

from ..core.config import settings


class ClickhouseService:
    def __init__(self, batch_size, flush_interval):
        self._client = Client(host=settings.clickhouse.host)
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batches = defaultdict(list)
        self.last_flush_time = time()

    def add_to_batch(self, table_name: str, data: dict):
        """Добавляет данные в батч для указанной таблицы."""
        self.batches[table_name].append(data)

    def is_batch_full(self, table_name: str) -> bool:
        return len(self.batches[table_name]) >= self.batch_size

    def flush(self):
        """Принудительно отправляет все накопленные данные в ClickHouse."""
        for table_name in list(self.batches.keys()):
            self.flush_table(table_name)

    def flush_table(self, table_name: str):
        """Отправляет данные для конкретной таблицы в ClickHouse."""
        if not self.batches[table_name]:
            return
        keys = self.batches[table_name][0].keys()
        values = [list(item.values()) for item in self.batches[table_name]]
        keys_string = ', '.join(keys)
        self._client.execute(
            f'INSERT INTO ugc.{table_name} ({keys_string}) VALUES',
            values
        )
        self.batches[table_name].clear()

    def check_auto_flush(self):
        """Проверяет, требуется ли автоматическая отправка накопленных данных."""
        current_time = time()
        if current_time - self.last_flush_time > self.flush_interval:
            self.flush()
            self.last_flush_time = current_time
