from __future__ import annotations

from typing import Optional, Protocol

from ...manager import BaseUserManager
from ...models import UP, ID


class StrategyDestroyNotSupportedError(Exception):
    pass


class Strategy(Protocol[UP, ID]):
    async def read_token(
            self, token: Optional[str], user_manager: BaseUserManager[UP, ID]
    ) -> Optional[UP]: ...  # pragma: no cover

    async def write_token(self, user: UP) -> str: ...  # pragma: no cover

    async def destroy_token(
            self, token: str, user: UP
    ) -> None: ...  # pragma: no cover
