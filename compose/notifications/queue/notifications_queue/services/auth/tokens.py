from __future__ import annotations

import abc
from typing import Any, Annotated

import httpx
from taskiq import TaskiqDepends

from .models import AuthTokens
from ...core import settings
from ...dependencies.tasks import HTTPXClientTaskiqDep


class AuthTokensProcessor:
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

        response = await LoginRequest(
            httpx_client=self.httpx_client,
            username=self.user_login,
            password=self.user_password,
        ).send_request()

        self._auth_tokens = AuthTokens.model_validate(response.json())
        return self._auth_tokens

    async def refresh(self) -> AuthTokens:
        if self._auth_tokens is None:
            return await self.login()

        response = await RefreshRequest(
            httpx_client=self.httpx_client,
            refresh_token=self._auth_tokens.refresh_token,
        ).send_request()

        self._auth_tokens = AuthTokens.model_validate(response.json())
        return self._auth_tokens


class AuthServiceRequest(abc.ABC):
    httpx_client: httpx.AsyncClient
    x_request_id: str

    def __init__(self,
                 *,
                 httpx_client: httpx.AsyncClient,
                 x_request_id: str | None = None) -> None:
        self.httpx_client = httpx_client
        self.x_request_id = x_request_id or settings.auth.x_request_id

    async def send_request(self) -> httpx.Response:
        return await self._process_request()

    async def _process_request(self, *, headers: dict | None = None) -> httpx.Response:
        headers = {
            **self.get_headers(),
            **(headers or {}),
        }
        response = await self._send_request(headers=headers)
        response.raise_for_status()
        return response

    def get_headers(self) -> dict:
        return {
            'X-Request-Id': self.x_request_id,
        }

    @abc.abstractmethod
    async def _send_request(self, *, headers: dict) -> httpx.Response:
        ...


class LoginRequest(AuthServiceRequest):
    username: str
    password: str

    def __init__(self, *, username: str, password: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.username = username
        self.password = password

    async def _send_request(self, *, headers: dict) -> httpx.Response:
        return await self.httpx_client.post(
            url=settings.auth.get_login_url(),
            data={
                'grant_type': 'password',
                'username': self.username,
                'password': self.password,
            },
            headers=headers,
        )


class RefreshRequest(AuthServiceRequest):
    refresh_token: str

    def __init__(self, *, refresh_token: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.refresh_token = refresh_token

    async def _send_request(self, *, headers: dict) -> httpx.Response:
        return await self.httpx_client.post(
            url=settings.auth.get_refresh_url(),
            data={
                'refresh_token': self.refresh_token,
            },
            headers=headers,
        )


async def get_auth_tokens_processor(httpx_client: HTTPXClientTaskiqDep) -> AuthTokensProcessor:
    return AuthTokensProcessor(
        httpx_client=httpx_client,
        user_login=settings.auth.superuser_login,
        user_password=settings.auth.superuser_password,
    )


AuthTokensProcessorTaskiqDep = Annotated[AuthTokensProcessor, TaskiqDepends(get_auth_tokens_processor)]
