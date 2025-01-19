from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .base import Strategy
from .jwt import JWTStrategy
from ......core import settings


async def get_access_strategy() -> Strategy:
    return JWTStrategy(
        secret=settings.auth.secret_key,
        lifetime_seconds=settings.auth.access_jwt_lifetime,
        token_audience=['users:access'],
    )


async def get_refresh_strategy() -> Strategy:
    return JWTStrategy(
        secret=settings.auth.secret_key,
        lifetime_seconds=settings.auth.refresh_jwt_lifetime,
        token_audience=['users:refresh'],
    )


AccessStrategyDep = Annotated[Strategy, Depends(get_access_strategy)]
RefreshStrategyDep = Annotated[Strategy, Depends(get_refresh_strategy)]
