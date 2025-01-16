from fastapi import APIRouter, Depends, HTTPException, Request, status

from .common import ErrorCode, ErrorModel
from .. import exceptions
from ..authentication import Authenticator
from ..manager import BaseUserManager, UserManagerDependency
from ..models import UP, ID
from ..schemas import U, UU


def get_users_router(
        get_user_manager: UserManagerDependency[UP, ID],
        user_schema: type[U],
        user_update_schema: type[UU],
        authenticator: Authenticator[UP, ID],
) -> APIRouter:
    """Generate a router with the authentication routes."""
    router = APIRouter()

    get_current_user = authenticator.current_user()

    @router.get(
        "/me",
        response_model=user_schema,
        name="users:current_user",
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token.",
            },
        },
    )
    async def me(
            user: UP = Depends(get_current_user),
    ):
        return user_schema.model_validate(user)

    @router.patch(
        "/me",
        response_model=user_schema,
        dependencies=[Depends(get_current_user)],
        name="users:patch_current_user",
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token.",
            },
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
                                "summary": "A user with this email already exists.",
                                "value": {
                                    "detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS
                                },
                            },
                            ErrorCode.UPDATE_USER_INVALID_PASSWORD: {
                                "summary": "Password validation failed.",
                                "value": {
                                    "detail": {
                                        "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                                        "reason": "Password should be"
                                                  "at least 3 characters",
                                    }
                                },
                            },
                        }
                    }
                },
            },
        },
    )
    async def update_me(
            request: Request,
            user_update: user_update_schema,  # type: ignore
            user: UP = Depends(get_current_user),
            user_manager: BaseUserManager[UP, ID] = Depends(get_user_manager),
    ):
        try:
            user = await user_manager.update(
                user_update, user, safe=True,
            )
            return user_schema.model_validate(user)
        except exceptions.InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )
        except exceptions.UserAlreadyExists:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
            )

    return router
