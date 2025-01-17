from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from .base import (
    Transport,
    TransportLogoutNotSupportedError,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='v1/jwt/login', auto_error=False)
Oauth2TokenDep = Annotated[str, Depends(oauth2_scheme)]


class BearerResponse(BaseModel):
    access_token: str
    token_type: str


class BearerTransport(Transport):
    async def get_login_response(self, token: str) -> Response:
        bearer_response = BearerResponse(access_token=token, token_type="bearer")
        return JSONResponse(bearer_response.model_dump())

    async def get_logout_response(self) -> Response:
        raise TransportLogoutNotSupportedError()
