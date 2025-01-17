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
from ....openapi import OpenAPIResponseType

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

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        return {
            status.HTTP_200_OK: {
                "model": BearerResponse,
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1"
                                            "c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2Z"
                                            "DMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS"
                                            "11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ."
                                            "M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI",
                            "token_type": "bearer",
                        }
                    }
                },
            },
        }

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        return {}
