from __future__ import annotations

import uuid
from typing import Any

from .....models.sqlalchemy import User


class BaseUserDatabase:
    """Base adapter for retrieving, creating and updating users from a database."""

    async def get(self, id: uuid.UUID) -> User | None:
        """Get a single user by id."""
        raise NotImplementedError()

    async def get_by_login(self, login: str) -> User | None:
        """Get a single user by login."""
        raise NotImplementedError()

    async def create(self, create_dict: dict[str, Any]) -> User | None:
        """Create a user."""
        raise NotImplementedError()

    async def update(self, user: User | None, update_dict: dict[str, Any]) -> User:
        """Update a user."""
        raise NotImplementedError()

    async def delete(self, user: User) -> None:
        """Delete a user."""
        raise NotImplementedError()
