from __future__ import annotations

import uuid
from typing import Annotated, TypeVar

from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from ..db.sqlalchemy import AsyncSessionDep, AsyncSession, AuthBase
from ..schemas.role import RoleCreateDto, RoleInDB, RoleUpdateDto
from ..models.sqlalchemy import Role
from sqlalchemy import select, delete, update

ModelType = TypeVar('ModelType', bound=AuthBase)

class RoleRepository:
    _db: AsyncSession

    def __init__(self, db: AsyncSession):
        self._db = db

    async def add(self, role_create: RoleCreateDto) -> RoleInDB:
        role_dto = jsonable_encoder(role_create)
        role = Role(**role_dto)
        self._db.add(role)

        await self._db.commit()
        await self._db.refresh(role)

        return role

    async def update(self, id: uuid.UUID, role_update: RoleUpdateDto):
        fields = role_update.model_dump(exclude_unset=True)
        statement = update(Role).where(Role.id == id).values(fields)

        await self._db.execute(statement)
        await self._db.commit()

    async def findByCode(self, code: str) -> RoleInDB | None:
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

        await self._db.execute(query)
        await self._db.commit()


async def get_role_repository(db: AsyncSessionDep):
    return RoleRepository(db)

RoleRepositoryDep = Annotated[RoleRepository, Depends(get_role_repository)]
