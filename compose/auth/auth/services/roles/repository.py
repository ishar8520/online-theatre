from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError

from ...db.sqlalchemy import AsyncSession, AsyncSessionDep
from ...models.sqlalchemy import Role
from ..base.exceptions import AddError, DeleteError, UpdateError
from .models import RoleCreateDto, RoleInDB, RoleUpdateDto



class RoleRepository:
    _db: AsyncSession

    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, role_create: RoleCreateDto) -> RoleInDB:
        role_dto = jsonable_encoder(role_create)
        role = Role(**role_dto)
        self._db.add(role)

        try:
            await self._db.commit()
            await self._db.refresh(role)
        except SQLAlchemyError:
            await self._db.rollback()
            raise AddError

        return role

    async def update(self, id: uuid.UUID, role_update: RoleUpdateDto):
        fields = role_update.model_dump(exclude_unset=True)
        statement = update(Role).where(Role.id == id).values(fields)

        try:
            await self._db.execute(statement)
            await self._db.commit()
        except SQLAlchemyError:
            await self._db.rollback()
            raise UpdateError

    async def get_by_code(self, code: str) -> RoleInDB | None:
        statement = select(Role).where(Role.code == code)
        result = await self._db.execute(statement)
        return result.scalar_one_or_none()

    async def get(self, id: uuid.UUID) -> RoleInDB | None:
        statement = select(Role).where(Role.id == id)
        result = await self._db.execute(statement)
        return result.scalar_one_or_none()

    async def get_list(self) -> list[RoleInDB]:
        statement = select(Role)
        result = await self._db.execute(statement)
        return result.scalars().all()

    async def delete(self, id: uuid.UUID):
        query = delete(Role).where(Role.id == id)

        try:
            await self._db.execute(query)
            await self._db.commit()
        except SQLAlchemyError:
            await self._db.rollback()
            raise DeleteError


async def get_role_repository(db: AsyncSessionDep):
    return RoleRepository(db)

RoleRepositoryDep = Annotated[RoleRepository, Depends(get_role_repository)]
