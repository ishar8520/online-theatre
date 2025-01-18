from __future__ import annotations

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from ..settings import settings
from ..utils.auth.sqlalchemy import AuthBase

auth = settings.auth_postgresql
DATABASE_URL = f"postgresql+asyncpg://{auth.username}:{auth.password}@{auth.host}:{auth.port}/{auth.database}"


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def async_session(async_engine):
    async_session_maker = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="module", autouse=True)
async def clean_tables(async_session):
    for table in reversed(AuthBase.metadata.sorted_tables):
        await async_session.execute(
            text(f"TRUNCATE TABLE auth.{table.name} RESTART IDENTITY CASCADE")
        )
    await async_session.commit()


@pytest_asyncio.fixture(scope="module", autouse=True)
async def clean_tables(async_session):
    for table in reversed(AuthBase.metadata.sorted_tables):
        await async_session.execute(
            text(f"TRUNCATE TABLE auth.{table.name} RESTART IDENTITY CASCADE")
        )
    await async_session.commit()
