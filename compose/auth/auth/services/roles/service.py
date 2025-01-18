from __future__ import annotations

import uuid
from typing import Annotated
from fastapi import Depends

from .exceptions import DuplicateRoleTypeError
from .repository import (
    RoleRepositoryDep,
    RoleRepository
)
from .models import (
    RoleInDB,
    RoleCreateDto,
    RoleUpdateDto
)


class RoleService:
    _repository: RoleRepository

    def __init__(self, repository: RoleRepository):
        self._repository = repository

    async def create(self, role_create: RoleCreateDto) -> RoleInDB:
        role_existed = await self._repository.get_by_code(role_create.code)
        if role_existed is not None:
            raise DuplicateRoleTypeError

        return await self._repository.create(role_create)

    async def update(self, id: uuid.UUID, role_update: RoleUpdateDto) -> RoleInDB | None:
        if role_update.code is not None:
            role = await self._repository.get_by_code(role_update.code)
            if role is not None and role.id != id:
                raise DuplicateRoleTypeError

        await self._repository.update(id, role_update)
        return await self._repository.get(id)

    async def delete(self, id: uuid.UUID):
        role = await self._repository.get(id)
        if role is None:
            return None

        await self._repository.delete(id)
        return role

    async def get(self, id: uuid.UUID) -> RoleInDB:
        return await self._repository.get(id)

    async def get_list(self) -> list[RoleInDB]:
        return await self._repository.get_list()


async def get_role_service(repository: RoleRepositoryDep) -> RoleService:
    return RoleService(repository)

RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
