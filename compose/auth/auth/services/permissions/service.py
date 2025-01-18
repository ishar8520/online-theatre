from __future__ import annotations

import uuid
from typing import Annotated
from fastapi import Depends

from .exceptions import DuplicateUserPermissionError
from .models import (
    CreatePermissionDto,
    PermissionInDb,
    DeletePermission
)
from .repository import PermissionRepository, PermissionRepositoryDep


class PermissionService:
    _repository: PermissionRepository

    def __init__(self, repository: PermissionRepository):
        self._repository = repository

    async def assign(self, permission: CreatePermissionDto) -> PermissionInDb:
        # todo search user

        user_permission = await self._repository.get_by_user_role(
            user_id=permission.user_id,
            role_id=permission.role_id
        )
        if user_permission is not None:
            raise DuplicateUserPermissionError

        return await self._repository.add(permission)

    async def get_by_user(self, user_id: uuid.UUID) -> [PermissionInDb]:
        return await self._repository.get_by_user(user_id)

    async def revoke(self, id: uuid.UUID) -> DeletePermission | None:
        user_permission = await self._repository.get(id)
        if user_permission is None:
            return None

        await self._repository.delete(id)
        return user_permission


async def get_permission_service(
        repository: PermissionRepositoryDep
) -> PermissionService:
    return PermissionService(repository)

PermissionServiceDep = Annotated[
    PermissionService,
    Depends(get_permission_service)
]
