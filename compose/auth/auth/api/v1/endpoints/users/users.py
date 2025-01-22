from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from .common import ErrorCode, ErrorModel
from .....services.users import (
    CurrentUserDep,
    UserManagerDep,
    UserRead,
    UserUpdate,
    UserAlreadyExists,
)
from .....services.users.authentication.login_history.dependencies import PageDep
from .....services.users.authentication.login_history.models import LoginHistoryInDb
from .....services.users.authentication.login_history.service import LoginHistoryServiceDep

router = APIRouter()


@router.get(
    "/me",
    response_model=UserRead,
    name='users:current_user',
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token is invalid or missing.",
        },
    },
)
async def me(user: CurrentUserDep):
    return UserRead.model_validate(user, from_attributes=True)


@router.patch(
    "/me",
    response_model=UserRead,
    name='users:patch_current_user',
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token is invalid or missing.",
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
        user: CurrentUserDep,
        user_update: UserUpdate,
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


@router.get(
    "/get_login_history",
    response_model=list[LoginHistoryInDb],
    status_code=status.HTTP_200_OK,
    name="users:history_login_current_user"
)
async def get_login_history(
        login_history_service: LoginHistoryServiceDep,
        page: PageDep,
        user: CurrentUserDep,
):
    return await login_history_service.get_list(user.id, page)
