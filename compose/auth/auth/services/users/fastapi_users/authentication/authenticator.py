from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status

from .backend import (
    AuthenticationBackend,
    AuthenticationBackendDep,
    TokenDep,
)
from ..manager import (
    UserManager,
    UserManagerDep,
)
from .....models.sqlalchemy import User


class DuplicateBackendNamesError(Exception):
    pass


class Authenticator:
    backend: AuthenticationBackend

    def __init__(
            self,
            backend: AuthenticationBackend,
            user_manager: UserManager,
    ):
        self.backend = backend
        self.user_manager = user_manager

    async def authenticate(self,
                           *,
                           token: str,
                           optional: bool = False,
                           superuser: bool = False) -> User:
        user = await self.backend.authenticate(token=token, user_manager=self.user_manager)
        status_code = status.HTTP_401_UNAUTHORIZED

        if user:
            status_code = status.HTTP_403_FORBIDDEN

            if superuser and not user.is_superuser:
                user = None

        if not user and not optional:
            raise HTTPException(status_code=status_code)

        return user


async def get_authenticator(backend: AuthenticationBackendDep,
                            user_manager: UserManagerDep) -> Authenticator:
    return Authenticator(
        backend=backend,
        user_manager=user_manager,
    )


AuthenticatorDep = Annotated[Authenticator, Depends(get_authenticator)]


async def get_current_user(token: TokenDep, authenticator: AuthenticatorDep) -> User | None:
    return await authenticator.authenticate(token=token)


async def get_current_user_token(token: TokenDep, authenticator: AuthenticatorDep) -> tuple[User | None, str]:
    return await authenticator.authenticate(token=token), token
