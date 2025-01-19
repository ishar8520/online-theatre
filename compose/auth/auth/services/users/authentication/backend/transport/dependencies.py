from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from .base import Transport
from .bearer import BearerTransport

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='v1/jwt/login', auto_error=False)
Oauth2TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_token(token: Oauth2TokenDep) -> str:
    return token


async def get_transport() -> Transport:
    return BearerTransport()


TokenDep = Annotated[str, Depends(get_token)]
TransportDep = Annotated[Transport, Depends(get_transport)]
