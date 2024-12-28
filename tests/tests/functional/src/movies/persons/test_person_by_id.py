from __future__ import annotations

import uuid
from collections.abc import Iterable
from typing import Any
from urllib.parse import urljoin

import aiohttp
import pytest

from ....settings import settings
from ....utils.api import models as api_models
from ....utils.elasticsearch import ElasticsearchIndex
from ....utils.elasticsearch.models import (
    Person,
    PersonFilmRelation,
)
from ....utils.redis import RedisCache


class BasePersonByIdTestRunner:
    redis_cache: RedisCache
    elasticsearch_index: ElasticsearchIndex[Person]
    aiohttp_session: aiohttp.ClientSession
    persons_count: int

    def __init__(self,
                 *,
                 redis_cache: RedisCache,
                 elasticsearch_index: ElasticsearchIndex[Person],
                 aiohttp_session: aiohttp.ClientSession,
                 persons_count: int = 3) -> None:
        self.elasticsearch_index = elasticsearch_index
        self.aiohttp_session = aiohttp_session
        self.redis_cache = redis_cache
        self.persons_count = persons_count

    async def run(self) -> None:
        persons = list(self.create_persons())
        await self.save_persons_to_elasticsearch(persons=persons)

        person = self.get_person(persons=persons)
        person_id = person.id if person is not None else None

        person_result_data = await self.get_person_result(person_id=person_id)
        self.validate_person_result(person=person, person_result_data=person_result_data)

        await self.elasticsearch_index.delete_index()

        person_result_data = await self.get_person_result(person_id=person_id)
        self.validate_person_result(person=person, person_result_data=person_result_data)

        await self.redis_cache.clear()

        person_result_data = await self.get_person_result(person_id=person_id, expected_status=404)
        assert person_result_data is None

    def create_persons(self) -> Iterable[Person]:
        return self._generate_persons(count=self.persons_count)

    def _generate_persons(self, *, count: int = 1) -> Iterable[Person]:
        available_roles = ['director', 'actor', 'writer']

        for i in range(1, count + 1):
            yield Person(
                full_name=f'Персона {i}',
                films=[
                    PersonFilmRelation(
                        roles=[available_roles[(i - 1) % 3]],
                    ),
                ],
            )

    async def save_persons_to_elasticsearch(self, *, persons: list[Person]) -> None:
        if not persons:
            return

        await self.elasticsearch_index.load_documents(documents=persons)

    def get_person(self, *, persons: list[Person]) -> Person | None:
        if not persons:
            return None

        return persons[0]

    async def get_person_result(self, *, person_id: uuid.UUID | None, expected_status: int = 200) -> dict | None:
        if person_id is None:
            return None

        return await self._download_person(person_id=person_id, expected_status=expected_status)

    async def _download_person(self, *, person_id: uuid.UUID, expected_status: int = 200) -> dict | None:
        response_data = await self._get_person_response_data(
            person_id=str(person_id),
            expected_status=expected_status,
        )

        if expected_status == 404:
            return None

        return response_data

    async def _get_person_response_data(self,
                                        *,
                                        person_id: str,
                                        expected_status: int = 200) -> Any:
        person_by_id_api_url = urljoin(settings.movies_api_url, f'v1/persons/{person_id}')

        async with self.aiohttp_session.get(person_by_id_api_url) as response:
            assert response.status == expected_status
            response_data = await response.json()

        return response_data

    def validate_person_result(self, *, person: Person | None, person_result_data: dict | None) -> None:
        if person is None:
            assert person_result_data is None
            return

        expected_person_result = api_models.Person(**person.model_dump())
        expected_person_result_data = expected_person_result.model_dump(mode='json', by_alias=True)

        assert person_result_data == expected_person_result_data


class PersonByIdTestRunner(BasePersonByIdTestRunner):
    pass


class PersonDoesNotExistTestRunner(BasePersonByIdTestRunner):
    def get_person(self, *, persons: list[Person]) -> Person | None:
        return None

    async def get_person_result(self, *, person_id: uuid.UUID | None, expected_status: int = 200) -> dict | None:
        await self._download_person(
            person_id=uuid.uuid4(),
            expected_status=404,
        )
        await self._get_person_response_data(
            person_id='invalid',
            expected_status=422,
        )

        return None


@pytest.mark.asyncio(loop_scope='session')
async def test_person_by_id(
        redis_cache,
        create_elasticsearch_index,
        aiohttp_session,
) -> None:
    elasticsearch_index = await create_elasticsearch_index(index_name='persons')

    await PersonByIdTestRunner(
        redis_cache=redis_cache,
        elasticsearch_index=elasticsearch_index,
        aiohttp_session=aiohttp_session,
    ).run()


@pytest.mark.asyncio(loop_scope='session')
async def test_person_does_not_exist(
        redis_cache,
        create_elasticsearch_index,
        aiohttp_session,
) -> None:
    elasticsearch_index = await create_elasticsearch_index(index_name='persons')

    await PersonDoesNotExistTestRunner(
        redis_cache=redis_cache,
        elasticsearch_index=elasticsearch_index,
        aiohttp_session=aiohttp_session,
    ).run()
