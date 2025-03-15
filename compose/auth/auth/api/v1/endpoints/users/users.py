from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status

from .common import ErrorCode, ErrorModel
from .....services.users import (
    CurrentUserDep,
    CurrentSuperuserDep,
    UserManagerDep,
    UserRead,
    UserUpdate,
    UserDoesNotExist,
    UserAlreadyExists,
)
from .....services.users.authentication.login_history.dependencies import PageDep
from .....services.users.authentication.login_history.models import LoginHistoryInDb
from .....services.users.authentication.login_history.service import LoginHistoryServiceDep

router = APIRouter()


@router.get(
    '/me',
    name='users:get_current_user',
    response_model=UserRead,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Token is invalid or missing.',
        },
    },
)
async def get_current_user(user: CurrentUserDep) -> UserRead:
    return UserRead.model_validate(user, from_attributes=True)


@router.patch(
    '/me',
    name='users:patch_current_user',
    response_model=UserRead,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Token is invalid or missing.',
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': ErrorModel,
            'content': {
                'application/json': {
                    'examples': {
                        ErrorCode.UPDATE_USER_LOGIN_ALREADY_EXISTS: {
                            'summary': 'A user with this login already exists.',
                            'value': {
                                'detail': ErrorCode.UPDATE_USER_LOGIN_ALREADY_EXISTS
                            },
                        },
                    }
                }
            },
        },
    },
)
async def patch_current_user(user: CurrentUserDep,
                             user_update: UserUpdate,
                             user_manager: UserManagerDep) -> UserRead:
    try:
        user = await user_manager.update(user_update, user)
    except UserAlreadyExists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.UPDATE_USER_LOGIN_ALREADY_EXISTS,
        )

    return UserRead.model_validate(user, from_attributes=True)


@router.get(
    '/{user_id}',
    name='users:get_user',
    response_model=UserRead,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Missing token or inactive user.',
        },
        status.HTTP_403_FORBIDDEN: {
            'description': 'Not a superuser.',
        },
        status.HTTP_404_NOT_FOUND: {
            'description': 'The user does not exist.',
        },
    },
)
async def get_user(user_id: uuid.UUID,
                   user_manager: UserManagerDep,
                   _current_superuser: CurrentSuperuserDep) -> UserRead:
    try:
        user = await user_manager.get(user_id)
    except UserDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorCode.USER_DOES_NOT_EXIST,
        )

    return UserRead.model_validate(user, from_attributes=True)


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
    login_history_list = await login_history_service.get_list(user.id, page)
    return [
        LoginHistoryInDb.model_validate(login_history, from_attributes=True)
        for login_history in login_history_list
    ]
