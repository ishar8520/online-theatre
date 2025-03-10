from __future__ import annotations

from collections.abc import Callable, Awaitable, AsyncGenerator

import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ..settings import settings


@pytest_asyncio.fixture(scope='session')
async def mongo_client_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    client: AsyncIOMotorClient = AsyncIOMotorClient(f'mongodb://{settings.mongo.host}:{settings.mongo.port}')
    db = client.get_database(settings.mongo.db)
    yield db
    client.close()


@pytest_asyncio.fixture(scope='function', autouse=True)
async def clear_mongo(
        mongo_client_db: AsyncIOMotorDatabase
) -> AsyncGenerator[Callable[[], Awaitable[None]]]:

    async def _clear_mongo() -> None:
        collection_name_list = await mongo_client_db.list_collection_names()
        for name in collection_name_list:
            await mongo_client_db.get_collection(name).delete_many({})

    await _clear_mongo()
    yield _clear_mongo
    await _clear_mongo()
