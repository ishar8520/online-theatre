from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase

from ..core import settings

auth_metadata_obj = MetaData(schema='auth')


class AuthBase(DeclarativeBase):
    metadata = auth_metadata_obj


engine = create_async_engine(settings.postgresql.engine_url, echo=settings.auth.sql_echo)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
