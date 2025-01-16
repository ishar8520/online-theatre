from __future__ import annotations

from typing import Protocol, TypeVar

ID = TypeVar("ID")


class UserProtocol(Protocol[ID]):
    """User protocol that ORM model should follow."""

    id: ID
    email: str
    hashed_password: str
    is_superuser: bool


UP = TypeVar("UP", bound=UserProtocol)
