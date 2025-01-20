from __future__ import annotations

from typing import Protocol

from ....manager import UserManager
from ......models.sqlalchemy import User


class StrategyDestroyNotSupportedError(Exception):
    pass


class InvalidToken(Exception):
    pass


class Strategy(Protocol):
    async def read_token(self, token: str, user_manager: UserManager) -> User | None: ...

    async def write_token(self, user: User) -> str: ...

    async def destroy_token(self, token: str, user: User) -> None: ...
