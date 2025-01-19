from __future__ import annotations

import uuid
from typing import Annotated
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .models import (
    LoginHistoryCreate,
    LoginHistoryInDb
)
from .....db.sqlalchemy import (
    AsyncSessionDep,
    AsyncSession
)
from .....models.sqlalchemy import LoginHistory


class LoginHistoryRepository:
    _db: AsyncSession

    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(
            self,
            login_history_create: LoginHistoryCreate
    ) -> LoginHistoryInDb:
        login_history_create_dto = jsonable_encoder(login_history_create)
        login_history_row = LoginHistory(**login_history_create_dto)
        self._db.add(login_history_row)

        try:
            await self._db.commit()
            await self._db.refresh(login_history_row)
        except SQLAlchemyError:
            await self._db.rollback()

        return login_history_row

    async def get_list_by_user(
            self,
            user_id: uuid.UUID
    ) -> list[LoginHistoryInDb]:
        statement = select(LoginHistory).where(LoginHistory.user_id == user_id)
        result = await self._db.execute(statement)
        return result.scalars().all()


async def get_login_history_repository(
        db: AsyncSessionDep
) -> LoginHistoryRepository:
    return LoginHistoryRepository(db)

LoginHistoryRepositoryDep = Annotated[
    LoginHistoryRepository,
    Depends(get_login_history_repository)
]
