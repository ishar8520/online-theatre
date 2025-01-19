from __future__ import annotations

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from ..settings import settings

auth = settings.auth_postgresql
DATABASE_URL = f'postgresql+asyncpg://{auth.username}:{auth.password}@{auth.host}:{auth.port}/{auth.database}'
TABLES = ['login_history', 'user_role', 'user', 'role']


@pytest_asyncio.fixture(scope='session')
async def async_engine():
    engine = create_async_engine(DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope='module')
async def async_session(async_engine):
    async_session_maker = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope='module')
async def clean_all_tables(async_session):
    for table in TABLES:
        await async_session.execute(
            text(f'TRUNCATE TABLE auth.{table} RESTART IDENTITY CASCADE')
        )
    await async_session.commit()

 
@pytest_asyncio.fixture(scope='module')
async def clean_all_tables_before(async_session):
    for table in TABLES:
        if table == 'user':
            query = f'DELETE FROM auth.user WHERE is_superuser != true'
        else:
            query = f'TRUNCATE TABLE auth.{table} RESTART IDENTITY CASCADE'
        await async_session.execute(
            text(query)
        )
    await async_session.commit()
    yield

@pytest_asyncio.fixture(scope='module')
async def clean_all_tables_after(async_session):
    yield
    for table in TABLES:
        if table == 'user':
            query = f'DELETE FROM auth.user WHERE is_superuser != true'
        else:
            query = f'TRUNCATE TABLE auth.{table} RESTART IDENTITY CASCADE'
        await async_session.execute(
            text(query)
        )
    await async_session.commit()
