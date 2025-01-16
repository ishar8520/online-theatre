from __future__ import annotations

from collections.abc import Sequence
from typing import Generic

from fastapi import APIRouter

from .authentication import AuthenticationBackend, Authenticator
from .manager import UserManagerDependency
from .models import UP, ID
from .router import (
    get_auth_router,
    get_register_router,
    get_reset_password_router,
    get_users_router,
)
from .schemas import U, UC, UU


class FastAPIUsers(Generic[UP, ID]):
    """
    Main object that ties together the component for users authentication.

    :param get_user_manager: Dependency callable getter to inject the
    user manager class instance.
    :param auth_backends: List of authentication backends.

    :attribute current_user: Dependency callable getter to inject authenticated user
    with a specific set of parameters.
    """

    authenticator: Authenticator[UP, ID]

    def __init__(
            self,
            get_user_manager: UserManagerDependency[UP, ID],
            auth_backends: Sequence[AuthenticationBackend[UP, ID]],
    ):
        self.authenticator = Authenticator(auth_backends, get_user_manager)
        self.get_user_manager = get_user_manager
        self.current_user = self.authenticator.current_user

    def get_register_router(
            self, user_schema: type[U], user_create_schema: type[UC]
    ) -> APIRouter:
        """
        Return a router with a register route.

        :param user_schema: Pydantic schema of a public user.
        :param user_create_schema: Pydantic schema for creating a user.
        """
        return get_register_router(
            self.get_user_manager, user_schema, user_create_schema
        )

    def get_reset_password_router(self) -> APIRouter:
        """Return a reset password process router."""
        return get_reset_password_router(self.get_user_manager)

    def get_auth_router(
            self,
            backend: AuthenticationBackend[UP, ID],
    ) -> APIRouter:
        """
        Return an auth router for a given authentication backend.

        :param backend: The authentication backend instance.
        """
        return get_auth_router(
            backend,
            self.get_user_manager,
            self.authenticator,
        )

    def get_users_router(
            self,
            user_schema: type[U],
            user_update_schema: type[UU],
    ) -> APIRouter:
        """
        Return a router with routes to manage users.

        :param user_schema: Pydantic schema of a public user.
        :param user_update_schema: Pydantic schema for updating a user.
        require the users to be verified or not. Defaults to False.
        """
        return get_users_router(
            self.get_user_manager,
            user_schema,
            user_update_schema,
            self.authenticator,
        )
