from __future__ import annotations

import abc
import uuid
from typing import Annotated, Any

import httpx
from fastapi import (
    Depends,
    status,
    HTTPException,
)

from .client import (
    AuthClient,
    AuthClientDep,
)
from .models import User


class AbstractAuthService(abc.ABC):
    @abc.abstractmethod
    async def get_user(self, *, user_id: uuid.UUID) -> User | None: ...


class AuthService(AbstractAuthService):
    auth_client: AuthClient

    def __init__(self, *, auth_client: AuthClient) -> None:
        self.auth_client = auth_client

    async def get_user(self, *, user_id: uuid.UUID) -> User | None:
        return await GetUserRequest(
            auth_client=self.auth_client,
            user_id=user_id,
        ).send_request()


class AuthServiceRequest[TResponse](abc.ABC):
    auth_client: AuthClient

    def __init__(self, *, auth_client: AuthClient) -> None:
        self.auth_client = auth_client

    async def send_request(self) -> TResponse:
        try:
            return await self._send_request()

        except httpx.HTTPError:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    @abc.abstractmethod
    async def _send_request(self) -> TResponse:
        ...


class GetUserRequest(AuthServiceRequest[User | None]):
    user_id: uuid.UUID

    def __init__(self, *, user_id: uuid.UUID, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.user_id = user_id

    async def _send_request(self) -> User | None:
        return await self.auth_client.get_user(user_id=self.user_id)


def get_auth_service(auth_client: AuthClientDep) -> AuthService:
    return AuthService(auth_client=auth_client)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
