from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from ....services.roles.exceptions import (AddError, DeleteError,
                                           DuplicateRoleTypeError, UpdateError)
from ....services.roles.models import (RoleCreateDto, RoleDelete, RoleInDB,
                                       RoleUpdateDto)
from ....services.roles.service import RoleServiceDep

router = APIRouter()


@router.post(
    "/add",
    response_model=RoleInDB,
    status_code=HTTPStatus.CREATED,
    summary="Create new role",
    description="Creation new role in service",
)
async def add(role: RoleCreateDto, role_service: RoleServiceDep) -> RoleInDB:
    try:
        created_role = await role_service.add(role)
    except DuplicateRoleTypeError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Duplicate role type"
        )
    except AddError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Add error"
        )

    return created_role


@router.put(
    "/update/{id}",
    response_model=RoleInDB,
    status_code=HTTPStatus.OK,
    summary="Update role",
    description="Update information about role",
)
async def update(
    id: uuid.UUID, role_update: RoleUpdateDto, role_service: RoleServiceDep
) -> RoleInDB | None:
    try:
        update_role = await role_service.update(id, role_update)
    except DuplicateRoleTypeError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Duplicate role type"
        )
    except UpdateError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Update error"
        )

    if update_role is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")

    return update_role


@router.delete(
    "/delete/{id}",
    response_model=RoleDelete,
    status_code=HTTPStatus.OK,
    summary="Delete role",
    description="Delete role in service",
)
async def delete(id: uuid.UUID, role_service: RoleServiceDep) -> RoleDelete:
    try:
        role = await role_service.delete(id)
    except DeleteError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Delete error"
        )

    if role is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")

    return role


@router.get(
    "/get/{id}",
    response_model=RoleInDB,
    status_code=HTTPStatus.OK,
    summary="Role details",
    description="Get description of role",
)
async def get(id: uuid.UUID, role_service: RoleServiceDep) -> RoleInDB:
    role = await role_service.get(id)
    if role is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")

    return role


@router.get(
    "/list",
    response_model=list[RoleInDB],
    status_code=HTTPStatus.OK,
    summary="List of roles",
    description="Get list of roles with description",
)
async def list(role_service: RoleServiceDep) -> list[RoleInDB]:
    return await role_service.list()
