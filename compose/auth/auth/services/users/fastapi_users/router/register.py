from fastapi import APIRouter, Depends, HTTPException, status

from .common import ErrorCode, ErrorModel
from .. import exceptions
from ..manager import BaseUserManager, UserManagerDependency
from ..models import UP, ID
from ..schemas import U, UC


def get_register_router(
        get_user_manager: UserManagerDependency[UP, ID],
        user_schema: type[U],
        user_create_schema: type[UC],
) -> APIRouter:
    """Generate a router with the register route."""
    router = APIRouter()

    @router.post(
        "/register",
        response_model=user_schema,
        status_code=status.HTTP_201_CREATED,
        name="register:register",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                                "summary": "A user with this login already exists.",
                                "value": {
                                    "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                                },
                            },
                        }
                    }
                },
            },
        },
    )
    async def register(
            user_create: user_create_schema,  # type: ignore
            user_manager: BaseUserManager[UP, ID] = Depends(get_user_manager),
    ):
        try:
            created_user = await user_manager.create(
                user_create, safe=True,
            )
        except exceptions.UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )

        return user_schema.model_validate(created_user)

    return router
