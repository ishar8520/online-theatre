from __future__ import annotations

import abc
import uuid
from typing import Any, Annotated

import httpx
from fastapi import (
    Depends,
    status,
)

from .models import (
    User,
)
from .token import (
    AuthTokenClient,
    AuthTokenClientDep,
)
from ...core import settings
from ...dependencies import HTTPXClientDep


class AuthClient:
    httpx_client: httpx.AsyncClient
    auth_token_client: AuthTokenClient

    def __init__(self,
                 *,
                 httpx_client: httpx.AsyncClient,
                 auth_token_client: AuthTokenClient) -> None:
        self.httpx_client = httpx_client
        self.auth_token_client = auth_token_client

    async def get_user(self, *, user_id: uuid.UUID) -> User | None:
        try:
            response = await GetUserRequest(
                httpx_client=self.httpx_client,
                auth_token_client=self.auth_token_client,
                user_id=user_id,
            ).send_request()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == status.HTTP_404_NOT_FOUND:
                return None

            raise

        return User.model_validate(response.json())


class AuthClientRequest(abc.ABC):
    httpx_client: httpx.AsyncClient
    auth_token_client: AuthTokenClient
    x_request_id: str

    def __init__(self,
                 *,
                 httpx_client: httpx.AsyncClient,
                 auth_token_client: AuthTokenClient,
                 x_request_id: str | None = None) -> None:
        self.httpx_client = httpx_client
        self.auth_token_client = auth_token_client
        self.x_request_id = x_request_id or 'notifications_queue'

    async def send_request(self) -> httpx.Response:
        auth_tokens = await self.auth_token_client.login()

        try:
            return await self._send_authenticated_request(token=auth_tokens.access_token)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == status.HTTP_401_UNAUTHORIZED:
                auth_tokens = await self.auth_token_client.refresh()
                return await self._send_authenticated_request(token=auth_tokens.access_token)
            else:
                raise

    async def _send_authenticated_request(self, *, token: str) -> httpx.Response:
        headers = self.get_headers(token=token)
        response = await self._send_request(headers=headers)
        response.raise_for_status()
        return response

    def get_headers(self, *, token: str) -> dict:
        return {
            'X-Request-Id': self.x_request_id,
            'Authorization': f'Bearer {token}',
        }

    @abc.abstractmethod
    async def _send_request(self, *, headers: dict) -> httpx.Response:
        ...


class GetUserRequest(AuthClientRequest):
    user_id: uuid.UUID

    def __init__(self, *, user_id: uuid.UUID, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.user_id = user_id

    async def _send_request(self, *, headers: dict) -> httpx.Response:
        user_url = settings.auth.get_user_url(user_id=self.user_id)

        return await self.httpx_client.get(
            url=user_url,
            headers=headers,
        )


def get_auth_client(httpx_client: HTTPXClientDep,
                    auth_token_client: AuthTokenClientDep) -> AuthClient:
    return AuthClient(
        httpx_client=httpx_client,
        auth_token_client=auth_token_client,
    )


AuthClientDep = Annotated[AuthClient, Depends(get_auth_client)]
