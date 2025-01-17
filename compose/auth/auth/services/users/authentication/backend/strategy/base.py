from __future__ import annotations

from typing import Optional, Protocol

from ....manager import UserManager
from ......models.sqlalchemy import User


class StrategyDestroyNotSupportedError(Exception):
    pass


class Strategy(Protocol):
    async def read_token(
            self, token: Optional[str], user_manager: UserManager
    ) -> Optional[User]: ...

    async def write_token(self, user: User) -> str: ...

    async def destroy_token(
            self, token: str, user: User
    ) -> None: ...
