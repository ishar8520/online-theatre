from __future__ import annotations

from typing import Annotated

import httpx
from taskiq import TaskiqDepends

from .models import AuthTokens
from ..http import HttpClient
from ...core import settings
from ...dependencies.tasks import HTTPXClientTaskiqDep


class AuthTokensProcessor:
    http_client: HttpClient
    user_login: str
    user_password: str

    _auth_tokens: AuthTokens | None

    def __init__(self,
                 *,
                 httpx_client: httpx.AsyncClient,
                 user_login: str,
                 user_password: str) -> None:
        self.http_client = HttpClient(
            httpx_client=httpx_client,
            base_url=settings.auth.api_v1_url,
        )
        self.user_login = user_login
        self.user_password = user_password

        self._auth_tokens = None

    async def login(self) -> AuthTokens:
        if self._auth_tokens is not None:
            return self._auth_tokens

        response = await self.http_client.post(
            settings.auth.get_login_url(),
            data={
                'grant_type': 'password',
                'username': self.user_login,
                'password': self.user_password,
            },
        )

        self._auth_tokens = AuthTokens.model_validate(response.json())
        return self._auth_tokens

    async def refresh(self) -> AuthTokens:
        if self._auth_tokens is None:
            return await self.login()

        response = await self.http_client.post(
            settings.auth.get_refresh_url(),
            data={
                'refresh_token': self._auth_tokens.refresh_token,
            },
        )

        self._auth_tokens = AuthTokens.model_validate(response.json())
        return self._auth_tokens


async def get_auth_tokens_processor(httpx_client: HTTPXClientTaskiqDep) -> AuthTokensProcessor:
    return AuthTokensProcessor(
        httpx_client=httpx_client,
        user_login=settings.auth.superuser_login,
        user_password=settings.auth.superuser_password,
    )


AuthTokensProcessorTaskiqDep = Annotated[AuthTokensProcessor, TaskiqDepends(get_auth_tokens_processor)]
