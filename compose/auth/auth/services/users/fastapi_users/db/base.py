from __future__ import annotations

from typing import Any, Generic, Optional

from ..models import ID, UP
from ..types import DependencyCallable


class BaseUserDatabase(Generic[UP, ID]):
    """Base adapter for retrieving, creating and updating users from a database."""

    async def get(self, id: ID) -> Optional[UP]:
        """Get a single user by id."""
        raise NotImplementedError()

    async def get_by_email(self, email: str) -> Optional[UP]:
        """Get a single user by email."""
        raise NotImplementedError()

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UP]:
        """Get a single user by OAuth account id."""
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
