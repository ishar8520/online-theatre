from __future__ import annotations

import abc
import uuid
from typing import Any, Annotated

import httpx
from fastapi import (
    status,
)
from taskiq import TaskiqDepends

from .models import (
    User,
)
from .tokens import (
    AuthTokensProcessor,
    AuthTokensProcessorTaskiqDep,
    AuthServiceRequest,
)
from ...core import settings
from ...dependencies.tasks import HTTPXClientTaskiqDep


class AuthServiceClient:
    httpx_client: httpx.AsyncClient
    auth_tokens_processor: AuthTokensProcessor

    def __init__(self,
                 *,
                 httpx_client: httpx.AsyncClient,
                 auth_tokens_processor: AuthTokensProcessor) -> None:
        self.httpx_client = httpx_client
        self.auth_tokens_processor = auth_tokens_processor

    async def get_user(self, *, user_id: uuid.UUID) -> User | None:
        try:
            response = await GetUserRequest(
                httpx_client=self.httpx_client,
                auth_tokens_processor=self.auth_tokens_processor,
                user_id=user_id,
            ).send_request()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == status.HTTP_404_NOT_FOUND:
                return None

            raise

        return User.model_validate(response.json())


class AuthenticatedRequest(AuthServiceRequest):
    auth_tokens_processor: AuthTokensProcessor

    def __init__(self, *, auth_tokens_processor: AuthTokensProcessor, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.auth_tokens_processor = auth_tokens_processor

    async def send_request(self) -> httpx.Response:
        auth_tokens = await self.auth_tokens_processor.login()

        try:
            return await self._send_authenticated_request(token=auth_tokens.access_token)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == status.HTTP_401_UNAUTHORIZED:
                auth_tokens = await self.auth_tokens_processor.refresh()
                return await self._send_authenticated_request(token=auth_tokens.access_token)
            else:
                raise

    async def _send_authenticated_request(self, *, token: str) -> httpx.Response:
        return await self._process_request(headers={
            'Authorization': f'Bearer {token}',
        })

    @abc.abstractmethod
    async def _send_request(self, *, headers: dict) -> httpx.Response:
        ...


class GetUserRequest(AuthenticatedRequest):
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


async def get_auth_service_client(httpx_client: HTTPXClientTaskiqDep,
                                  auth_tokens_processor: AuthTokensProcessorTaskiqDep) -> AuthServiceClient:
    return AuthServiceClient(
        httpx_client=httpx_client,
        auth_tokens_processor=auth_tokens_processor,
    )


AuthServiceClientTaskiqDep = Annotated[AuthServiceClient, TaskiqDepends(get_auth_service_client)]
