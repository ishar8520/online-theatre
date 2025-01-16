from __future__ import annotations

from typing import Any, Generic, Optional

from ..models import ID, UP
from ..types import DependencyCallable


class BaseUserDatabase(Generic[UP, ID]):
    """Base adapter for retrieving, creating and updating users from a database."""

    async def get(self, id: ID) -> Optional[UP]:
        """Get a single user by id."""
        raise NotImplementedError()

    async def get_by_login(self, login: str) -> Optional[UP]:
        """Get a single user by login."""
        raise NotImplementedError()

    async def create(self, create_dict: dict[str, Any]) -> UP:
        """Create a user."""
        raise NotImplementedError()

    async def update(self, user: UP, update_dict: dict[str, Any]) -> UP:
        """Update a user."""
        raise NotImplementedError()

    async def delete(self, user: UP) -> None:
        """Delete a user."""
        raise NotImplementedError()


UserDatabaseDependency = DependencyCallable[BaseUserDatabase[UP, ID]]
