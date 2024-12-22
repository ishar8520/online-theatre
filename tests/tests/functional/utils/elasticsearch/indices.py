from __future__ import annotations

import elasticsearch
import elasticsearch.helpers


class ElasticsearchIndex:
    client: elasticsearch.AsyncElasticsearch
    index_name: str
    index_data: dict

    index_created: bool

    def __init__(self,
                 *,
                 client: elasticsearch.AsyncElasticsearch,
                 index_name: str,
                 index_data: dict) -> None:
        self.client = client
        self.index_name = index_name
        self.index_data = index_data

        self.index_created = False

    async def create_index(self) -> None:
        await self.delete_index()

        try:
            await self.client.indices.create(index=self.index_name, body=self.index_data)
        except elasticsearch.BadRequestError as e:
            if e.error == 'resource_already_exists_exception':
                pass

        self.index_created = True

    async def delete_index(self) -> None:
        try:
            await self.client.indices.delete(index=self.index_name)
        except elasticsearch.NotFoundError as e:
            if e.error == 'index_not_found_exception':
                pass

        self.index_created = False
