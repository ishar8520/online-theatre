from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..authentication import AuthenticationBackend, Authenticator, Strategy
from ..manager import BaseUserManager, UserManagerDependency
from ..models import UP, ID
from ..openapi import OpenAPIResponseType
from ..router.common import ErrorCode, ErrorModel


def get_auth_router(
        backend: AuthenticationBackend[UP, ID],
        get_user_manager: UserManagerDependency[UP, ID],
        authenticator: Authenticator[UP, ID],
) -> APIRouter:
    """Generate a router with login/logout routes for an authentication backend."""
    router = APIRouter()
    get_current_user_token = authenticator.current_user_token()

    login_responses: OpenAPIResponseType = {
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
        **backend.transport.get_openapi_login_responses_success(),
    }

    @router.post(
        "/login",
        name=f"auth:{backend.name}.login",
        responses=login_responses,
    )
    async def login(
            credentials: OAuth2PasswordRequestForm = Depends(),
            user_manager: BaseUserManager[UP, ID] = Depends(get_user_manager),
            strategy: Strategy[UP, ID] = Depends(backend.get_strategy),
    ):
        user = await user_manager.authenticate(credentials)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )

        response = await backend.login(strategy, user)

        return response

    logout_responses: OpenAPIResponseType = {
        **{
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token."
            }
        },
        **backend.transport.get_openapi_logout_responses_success(),
    }

    @router.post(
        "/logout", name=f"auth:{backend.name}.logout", responses=logout_responses
    )
    async def logout(
            user_token: tuple[UP, str] = Depends(get_current_user_token),
            strategy: Strategy[UP, ID] = Depends(backend.get_strategy),
    ):
        user, token = user_token
        return await backend.logout(strategy, user, token)

    return router
