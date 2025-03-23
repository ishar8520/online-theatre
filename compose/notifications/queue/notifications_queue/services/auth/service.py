from __future__ import annotations

import abc
import datetime
import uuid
from typing import Annotated, Any

import httpx
from fastapi import (
    status,
    HTTPException,
)
from taskiq import TaskiqDepends

from .client import (
    AuthServiceClient,
    AuthServiceClientTaskiqDep,
)
from .models import User


class AbstractAuthService(abc.ABC):
    @abc.abstractmethod
    async def get_user(self, *, user_id: uuid.UUID) -> User | None: ...

    @abc.abstractmethod
    async def get_users_list(self,
                             *,
                             user_id: uuid.UUID | None = None,
                             user_created: datetime.datetime | None = None,
                             page_size: int | None = None) -> list[User]: ...


class AuthService(AbstractAuthService):
    auth_service_client: AuthServiceClient

    def __init__(self, *, auth_service_client: AuthServiceClient) -> None:
        self.auth_service_client = auth_service_client

    async def get_user(self, *, user_id: uuid.UUID) -> User | None:
        return await GetUserRequest(
            auth_service_client=self.auth_service_client,
            user_id=user_id,
        ).send_request()

    async def get_users_list(self,
                             *,
                             user_id: uuid.UUID | None = None,
                             user_created: datetime.datetime | None = None,
                             page_size: int | None = None) -> list[User]:
        return await GetUsersListRequest(
            auth_service_client=self.auth_service_client,
            user_id=user_id,
            user_created=user_created,
            page_size=page_size,
        ).send_request()


class AuthServiceRequest[TResponse](abc.ABC):
    auth_service_client: AuthServiceClient

    def __init__(self, *, auth_service_client: AuthServiceClient) -> None:
        self.auth_service_client = auth_service_client

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
        return await self.auth_service_client.get_user(user_id=self.user_id)


class GetUsersListRequest(AuthServiceRequest[list[User]]):
    user_id: uuid.UUID | None
    user_created: datetime.datetime | None
    page_size: int | None

    def __init__(self,
                 *,
                 user_id: uuid.UUID | None = None,
                 user_created: datetime.datetime | None = None,
                 page_size: int | None = None,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.user_id = user_id
        self.user_created = user_created
        self.page_size = page_size

    async def _send_request(self) -> list[User]:
        return await self.auth_service_client.get_users_list(
            user_id=self.user_id,
            user_created=self.user_created,
            page_size=self.page_size,
        )


async def get_auth_service(auth_service_client: AuthServiceClientTaskiqDep) -> AbstractAuthService:
    return AuthService(auth_service_client=auth_service_client)


AuthServiceTaskiqDep = Annotated[AbstractAuthService, TaskiqDepends(get_auth_service)]
