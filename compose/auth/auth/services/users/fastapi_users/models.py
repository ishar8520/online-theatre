from __future__ import annotations

from typing import Protocol, TypeVar

ID = TypeVar("ID")


class UserProtocol(Protocol[ID]):
    """User protocol that ORM model should follow."""

    id: ID
    login: str
    password: str
    is_superuser: bool


UP = TypeVar("UP", bound=UserProtocol)
