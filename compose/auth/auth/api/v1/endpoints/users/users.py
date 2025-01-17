from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from .common import ErrorCode, ErrorModel
from .....models.sqlalchemy import User
from .....services.users import (
    get_current_user,
    UserManagerDep,
    UserRead,
    UserUpdate,
    UserAlreadyExists,
)

router = APIRouter()


@router.get(
    "/me",
    response_model=UserRead,
    name='users:current_user',
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token.",
        },
    },
)
async def me(user: User = Depends(get_current_user)):
    return UserRead.model_validate(user, from_attributes=True)


@router.patch(
    "/me",
    response_model=UserRead,
    dependencies=[Depends(get_current_user)],
    name='users:patch_current_user',
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.UPDATE_USER_LOGIN_ALREADY_EXISTS: {
                            "summary": "A user with this login already exists.",
                            "value": {
                                "detail": ErrorCode.UPDATE_USER_LOGIN_ALREADY_EXISTS
                            },
                        },
                    }
                }
            },
        },
    },
)
async def update_me(
        *,
        user_update: UserUpdate,
        user: User = Depends(get_current_user),
        user_manager: UserManagerDep,
):
    try:
        user = await user_manager.update(user_update, user)
        return UserRead.model_validate(user, from_attributes=True)
    except UserAlreadyExists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.UPDATE_USER_LOGIN_ALREADY_EXISTS,
        )
