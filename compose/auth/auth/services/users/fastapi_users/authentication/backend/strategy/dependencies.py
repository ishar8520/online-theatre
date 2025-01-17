from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .base import Strategy
from .jwt import JWTStrategy
from .......core import settings


async def get_strategy() -> Strategy:
    return JWTStrategy(
        secret=settings.auth.secret_key,
        lifetime_seconds=settings.auth.jwt_lifetime,
    )


StrategyDep = Annotated[Strategy, Depends(get_strategy)]
