from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from admin_panel.core import settings

engine = create_async_engine(settings.postgresql.engine_url)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


AsyncSessionDep = Annotated[AsyncSession, Depends(get_postgres_session)]
