from __future__ import annotations

import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from ..settings import settings


@pytest_asyncio.fixture(scope='function', autouse=True)
async def clear_mongo():
    client = AsyncIOMotorClient(f'mongodb://{settings.mongo.host}:{settings.mongo.port}')
    db = client.get_database(settings.mongo.db)
    collection_name_list = await db.list_collection_names()
    for name in collection_name_list:
        await db.get_collection(name).delete_many({})
