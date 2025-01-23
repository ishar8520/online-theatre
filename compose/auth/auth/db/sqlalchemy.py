from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncConnection,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase

from ..core import settings

auth_metadata_obj = MetaData(schema='auth')


class AuthBase(DeclarativeBase):
    metadata = auth_metadata_obj


engine = create_async_engine(settings.postgresql.engine_url, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    connection: AsyncConnection

    async with engine.begin() as connection:
        await create_super_user(connection)


async def create_super_user(connection: AsyncConnection):
    from ..models.sqlalchemy import User
    from ..services.users.password import PasswordHelper

    superuser = {
        "login": settings.superuser.login,
        "password": PasswordHelper().hash(settings.superuser.password),
        "is_superuser": True
    }

    statement = insert(User).values(superuser)
    try:
        await connection.execute(statement=statement)
    except SQLAlchemyError:
        pass


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
