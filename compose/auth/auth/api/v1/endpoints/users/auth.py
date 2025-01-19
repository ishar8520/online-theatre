from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Form,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from .common import ErrorCode, ErrorModel
from .....services.users import (
    CurrentUserDep,
    TokenDep,
    AuthenticationBackendDep,
    UserManagerDep,
)

router = APIRouter()


@router.post(
    "/login",
    name='auth:login',
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.LOGIN_BAD_CREDENTIALS: {
                            "summary": "Bad credentials.",
                            "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                        },
                    },
                },
            },
        },
    },
)
async def login(*,
                credentials: OAuth2PasswordRequestForm = Depends(),
                user_manager: UserManagerDep,
                backend: AuthenticationBackendDep):
    user = await user_manager.authenticate(credentials)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )

    return await backend.login(user)


@router.post(
    "/logout",
    name='auth:logout',
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Token is invalid or missing.",
        },
    },
)
async def logout(user: CurrentUserDep,
                 token: TokenDep,
                 backend: AuthenticationBackendDep):
    return await backend.logout(user=user, token=token)


@router.post(
    '/refresh',
    name='auth:refresh',
)
async def refresh(refresh_token: Annotated[str, Form()],
                  user_manager: UserManagerDep,
                  backend: AuthenticationBackendDep):
    user = await backend.authenticate_refresh(user_manager=user_manager, token=refresh_token)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.REFRESH_INVALID_TOKEN,
        )

    return await backend.refresh(user=user, token=refresh_token)
