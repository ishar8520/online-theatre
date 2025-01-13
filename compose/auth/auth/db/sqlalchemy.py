from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncConnection,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.schema import CreateSchema

from ..core import settings

auth_metadata_obj = MetaData(schema='auth')


class AuthBase(DeclarativeBase):
    metadata = auth_metadata_obj


engine = create_async_engine(settings.postgresql.engine_url, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_tables() -> None:
    connection: AsyncConnection

    async with engine.begin() as connection:
        await connection.execute(CreateSchema('auth', if_not_exists=True))
        await connection.run_sync(AuthBase.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
