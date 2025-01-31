from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from ..db.base import BaseUserDatabase
from ....models.sqlalchemy import (
    User,
    OAuthAccount,
)


class SQLAlchemyUserDatabase(BaseUserDatabase):
    session: AsyncSession
    user_table: type[User]
    oauth_account_table: type[OAuthAccount]

    def __init__(self,
                 *,
                 session: AsyncSession,
                 user_table: type[User],
                 oauth_account_table: type[OAuthAccount]) -> None:
        self.session = session
        self.user_table = user_table
        self.oauth_account_table = oauth_account_table

    async def get(self, id: uuid.UUID) -> User | None:
        statement = select(self.user_table).where(self.user_table.id == id)
        return await self._get_user(statement)

    async def get_by_login(self, login: str) -> User | None:
        statement = select(self.user_table).where(self.user_table.login == login)
        return await self._get_user(statement)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(self.user_table).where(self.user_table.email == email)
        return await self._get_user(statement)

    async def get_by_oauth_account(self, *, oauth_name: str, account_id: str) -> User:
        statement = (
            select(self.user_table)
            .join(self.oauth_account_table)
            .where(self.oauth_account_table.oauth_name == oauth_name)
            .where(self.oauth_account_table.account_id == account_id)
        )
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

    async def add_oauth_account(self, user: User, create_dict: dict[str, Any]) -> User:
        await self.session.refresh(user)

        oauth_account = self.oauth_account_table(**create_dict)
        self.session.add(oauth_account)
        user.oauth_accounts.append(oauth_account)
        self.session.add(user)

        await self.session.commit()

        return user

    async def update_oauth_account(self,
                                   user: User,
                                   oauth_account: OAuthAccount,
                                   update_dict: dict[str, Any]) -> User:
        for key, value in update_dict.items():
            setattr(oauth_account, key, value)

        self.session.add(oauth_account)
        await self.session.commit()

        return user

    async def _get_user(self, statement: Select) -> Optional[User]:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()
