from __future__ import annotations

import uuid
from typing import Any, Generic, Optional

import jwt
from fastapi.security import OAuth2PasswordRequestForm

from . import exceptions
from .db import BaseUserDatabase
from .jwt import decode_jwt
from .models import UP, ID
from .password import PasswordHelper, PasswordHelperProtocol
from .schemas import UC, UU
from .types import DependencyCallable


class BaseUserManager(Generic[UP, ID]):
    """
    User management logic.

    :param user_db: Database adapter instance.
    """

    user_db: BaseUserDatabase[UP, ID]
    password_helper: PasswordHelperProtocol

    def __init__(
            self,
            user_db: BaseUserDatabase[UP, ID],
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

    async def get(self, id: ID) -> UP:
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

    async def get_by_email(self, user_email: str) -> UP:
        """
        Get a user by e-mail.

        :param user_email: E-mail of the user to retrieve.
        :raises UserNotExists: The user does not exist.
        :return: A user.
        """
        user = await self.user_db.get_by_email(user_email)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def create(
            self,
            user_create: UC,
            safe: bool = False,
    ) -> UP:
        """
        Create a user in database.

        :param user_create: The UserCreate model to create.
        :param safe: If True, sensitive values like is_superuser
        will be ignored during the creation, defaults to False.
        :raises UserAlreadyExists: A user already exists with the same e-mail.
        :return: A new user.
        """
        existing_user = await self.user_db.get_by_email(user_create.email)
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
            user_update: UU,
            user: UP,
            safe: bool = False,
    ) -> UP:
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
    ) -> Optional[UP]:
        """
        Authenticate and return a user following an email and a password.

        Will automatically upgrade password hash if necessary.

        :param credentials: The user credentials.
        """
        try:
            user = await self.get_by_email(credentials.username)
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

    async def _update(self, user: UP, update_dict: dict[str, Any]) -> UP:
        validated_update_dict = {}
        for field, value in update_dict.items():
            if field == "email" and value != user.email:
                try:
                    await self.get_by_email(value)
                    raise exceptions.UserAlreadyExists()
                except exceptions.UserNotExists:
                    validated_update_dict["email"] = value
            elif field == "password" and value is not None:
                validated_update_dict["password"] = self.password_helper.hash(
                    value
                )
            else:
                validated_update_dict[field] = value
        return await self.user_db.update(user, validated_update_dict)


UserManagerDependency = DependencyCallable[BaseUserManager[UP, ID]]
