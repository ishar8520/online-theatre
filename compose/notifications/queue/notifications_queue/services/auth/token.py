from __future__ import annotations

from typing import Annotated

import httpx
from taskiq import TaskiqDepends

from .models import AuthTokens
from ...core import settings
from ...dependencies.tasks import HTTPXClientTaskiqDep


class AuthTokenClient:
    httpx_client: httpx.AsyncClient
    user_login: str
    user_password: str

    _auth_tokens: AuthTokens | None

    def __init__(self,
                 *,
                 httpx_client: httpx.AsyncClient,
                 user_login: str,
                 user_password: str) -> None:
        self.httpx_client = httpx_client
        self.user_login = user_login
        self.user_password = user_password

        self._auth_tokens = None

    async def login(self) -> AuthTokens:
        if self._auth_tokens is not None:
            return self._auth_tokens

        response = await self.httpx_client.post(
            url=settings.auth.get_login_url(),
            data={
                'grant_type': 'password',
                'username': self.user_login,
                'password': self.user_password,
            },
            headers=self.get_headers(),
        )
        response.raise_for_status()

        self._auth_tokens = AuthTokens.model_validate(response.json())
        return self._auth_tokens

    async def refresh(self) -> AuthTokens:
        if self._auth_tokens is None:
            return await self.login()

        response = await self.httpx_client.post(
            url=settings.auth.get_refresh_url(),
            data={
                'refresh_token': self._auth_tokens.refresh_token,
            },
            headers=self.get_headers(),
        )
        response.raise_for_status()

        self._auth_tokens = AuthTokens.model_validate(response.json())
        return self._auth_tokens

    def get_headers(self) -> dict:
        return {
            'X-Request-Id': 'notifications_queue',
        }


async def get_auth_token_client(httpx_client: HTTPXClientTaskiqDep) -> AuthTokenClient:
    return AuthTokenClient(
        httpx_client=httpx_client,
        user_login=settings.auth.superuser_login,
        user_password=settings.auth.superuser_password,
    )


AuthTokenClientTaskiqDep = Annotated[AuthTokenClient, TaskiqDepends(get_auth_token_client)]
