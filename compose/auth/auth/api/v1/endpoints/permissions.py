from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import (
    APIRouter,
    HTTPException
)

from ....services.base.exceptions import (
    AddError,
    DeleteError
)
from ....services.permissions.exceptions import DuplicateUserPermissionError
from ....services.permissions.models import (
    CreatePermissionDto,
    PermissionInDb,
    DeletePermission
)
from ....services.permissions.service import PermissionServiceDep

router = APIRouter()


@router.post(
    '/assign',
    status_code=HTTPStatus.CREATED,
    summary='Assign permission',
    description='Addition user into role'
)
async def assign(
    permission: CreatePermissionDto,
    permission_service: PermissionServiceDep
):
    try:
        permission = await permission_service.assign(permission)
    except DuplicateUserPermissionError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Duplicate permission'
        )
    except AddError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Add error'
        )

    return permission


@router.get(
    '/get_by_user/{user_id}',
    status_code=HTTPStatus.OK,
    summary='Get permissions',
    description='Get list of roles for user'
)
async def get_by_user(
    user_id: uuid.UUID,
    permission_service: PermissionServiceDep
) -> list[PermissionInDb]:
    return await permission_service.get_by_user(user_id)


@router.delete(
    '/revoke/{id}',
    status_code=HTTPStatus.OK,
    summary='Revoke permissions',
    description='Deleting user from role'
)
async def revoke(
    id: uuid.UUID,
    permission_service: PermissionServiceDep
) -> DeletePermission | None:
    try:
        role = await permission_service.revoke(id)
    except DeleteError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Delete error'
        )

    if role is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Permission not found'
        )

    return role
