from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .base import Transport
from .bearer import (
    Oauth2TokenDep,
    BearerTransport,
)


async def get_token(token: Oauth2TokenDep) -> str:
    return token


async def get_transport() -> Transport:
    return BearerTransport()


TokenDep = Annotated[str, Depends(get_token)]
TransportDep = Annotated[Transport, Depends(get_transport)]
