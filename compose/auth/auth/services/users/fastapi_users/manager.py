from __future__ import annotations

import uuid
from typing import Any, Optional, Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from . import exceptions
from .db import (
    BaseUserDatabase,
    UserDatabaseDep,
)
from .password import PasswordHelper, PasswordHelperProtocol
from .schemas import UserCreate, UserUpdate
from ....models.sqlalchemy import User


class UserManager:
    """
    User management logic.

    :param user_db: Database adapter instance.
    """

    user_db: BaseUserDatabase
    password_helper: PasswordHelperProtocol

    def __init__(
            self,
            user_db: BaseUserDatabase,
            password_helper: Optional[PasswordHelperProtocol] = None,
    ):
        self.user_db = user_db
        if password_helper is None:
            self.password_helper = PasswordHelper()
        else:
            self.password_helper = password_helper  # pragma: no cover

    def parse_id(self, value: Any) -> uuid.UUID:
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(value)
        except ValueError as e:
            raise exceptions.InvalidID() from e

    async def get(self, id: uuid.UUID) -> User:
        """
        Get a user by id.

        :param id: Id. of the user to retrieve.
        :raises UserNotExists: The user does not exist.
        :return: A user.
        """
        user = await self.user_db.get(id)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def get_by_login(self, user_login: str) -> User:
        """
        Get a user by login.

        :param user_login: Login of the user to retrieve.
        :raises UserNotExists: The user does not exist.
        :return: A user.
        """
        user = await self.user_db.get_by_login(user_login)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def create(
            self,
            user_create: UserCreate,
            safe: bool = False,
    ) -> User:
        """
        Create a user in database.

        :param user_create: The UserCreate model to create.
        :param safe: If True, sensitive values like is_superuser
        will be ignored during the creation, defaults to False.
        :raises UserAlreadyExists: A user already exists with the same login.
        :return: A new user.
        """
        existing_user = await self.user_db.get_by_login(user_create.login)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        return created_user

    async def update(
            self,
            user_update: UserUpdate,
            user: User,
            safe: bool = False,
    ) -> User:
        """
        Update a user.

        Triggers the on_after_update handler on success

        :param user_update: The UserUpdate model containing
        the changes to apply to the user.
        :param user: The current user to update.
        :param safe: If True, sensitive values like is_superuser
        will be ignored during the update, defaults to False
        :return: The updated user.
        """
        if safe:
            updated_user_data = user_update.create_update_dict()
        else:
            updated_user_data = user_update.create_update_dict_superuser()
        updated_user = await self._update(user, updated_user_data)
        return updated_user

    async def authenticate(
            self, credentials: OAuth2PasswordRequestForm
    ) -> User | None:
        """
        Authenticate and return a user following a login and a password.

        Will automatically upgrade password hash if necessary.

        :param credentials: The user credentials.
        """
        try:
            user = await self.get_by_login(credentials.username)
        except exceptions.UserNotExists:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.password
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            await self.user_db.update(user, {"password": updated_password_hash})

        return user

    async def _update(self, user: User, update_dict: dict[str, Any]) -> User:
        validated_update_dict = {}

        for field, value in update_dict.items():
            if field == "login" and value != user.login:
                try:
                    await self.get_by_login(value)
                    raise exceptions.UserAlreadyExists()
                except exceptions.UserNotExists:
                    validated_update_dict["login"] = value
            elif field == "password" and value is not None:
                validated_update_dict["password"] = self.password_helper.hash(value)
            else:
                validated_update_dict[field] = value

        return await self.user_db.update(user, validated_update_dict)


async def get_user_manager(user_db: UserDatabaseDep) -> UserManager:
    return UserManager(user_db=user_db)


UserManagerDep = Annotated[UserManager, Depends(get_user_manager)]
