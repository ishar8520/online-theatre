from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from ..db.base import BaseUserDatabase
from ....models.sqlalchemy import User


class SQLAlchemyUserDatabase(BaseUserDatabase):
    """
    Database adapter for SQLAlchemy.

    :param session: SQLAlchemy session instance.
    :param user_table: SQLAlchemy user model.
    """

    session: AsyncSession
    user_table: type[User]

    def __init__(
            self,
            session: AsyncSession,
            user_table: type[User],
    ):
        self.session = session
        self.user_table = user_table

    async def get(self, id: uuid.UUID) -> User | None:
        statement = select(self.user_table).where(self.user_table.id == id)
        return await self._get_user(statement)

    async def get_by_login(self, login: str) -> User | None:
        statement = select(self.user_table).where(self.user_table.login == login)
        return await self._get_user(statement)

    async def create(self, create_dict: dict[str, Any]) -> User:
        user = self.user_table(**create_dict)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User, update_dict: dict[str, Any]) -> User:
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def _get_user(self, statement: Select) -> Optional[User]:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()
