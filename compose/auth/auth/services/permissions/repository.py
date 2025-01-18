from __future__ import annotations

import uuid
from typing import Annotated
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import (
    select,
    delete
)
from sqlalchemy.exc import SQLAlchemyError

from .models import (
    PermissionInDb,
    CreatePermissionDto
)
from ..base.exceptions import (
    AddError,
    DeleteError
)
from ...db.sqlalchemy import (
    AsyncSessionDep,
    AsyncSession
)
from ...models.sqlalchemy import UserRole


class PermissionRepository:
    _db: AsyncSession

    def __init__(self, db: AsyncSession):
        self._db = db

    async def add(self, permission_dto: CreatePermissionDto) -> PermissionInDb:
        permission_dto = jsonable_encoder(permission_dto)

        user_role = UserRole(**permission_dto)
        self._db.add(user_role)

        try:
            await self._db.commit()
            await self._db.refresh(user_role)
        except SQLAlchemyError:
            await self._db.rollback()
            raise AddError

        return user_role

    async def get_by_user_role(
            self, user_id: uuid.UUID,
            role_id: uuid.UUID
    ) -> PermissionInDb | None:
        statement = select(UserRole).where(
            UserRole.role_id == role_id,
            UserRole.user_id == user_id
        )
        result = await self._db.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: uuid.UUID) -> [PermissionInDb]:
        statement = select(UserRole).where(UserRole.user_id == user_id)
        result = await self._db.execute(statement)
        return result.scalars().all()

    async def get(self, id: uuid.UUID) -> PermissionInDb | None:
        statement = select(UserRole).where(UserRole.id == id)
        result = await self._db.execute(statement)
        return result.scalar_one_or_none()

    async def delete(self, id: uuid.UUID) -> None:
        query = delete(UserRole).where(UserRole.id == id)

        try:
            await self._db.execute(query)
            await self._db.commit()
        except SQLAlchemyError:
            await self._db.rollback()
            raise DeleteError


async def get_permission_repository(db: AsyncSessionDep):
    return PermissionRepository(db)

PermissionRepositoryDep = Annotated[
    PermissionRepository,
    Depends(get_permission_repository)
]
