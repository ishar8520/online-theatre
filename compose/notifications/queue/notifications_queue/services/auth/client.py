from __future__ import annotations

import datetime
import uuid
from typing import Any, Annotated

import httpx
from fastapi import (
    status,
)
from taskiq import TaskiqDepends

from .models import (
    AuthTokens,
    User,
    UsersListParams,
)
from .tokens import (
    AuthTokensProcessor,
    AuthTokensProcessorTaskiqDep,
)
from ..http import (
    HttpClient,
    HttpResponse,
)
from ...core import settings
from ...dependencies.tasks import HTTPXClientTaskiqDep


class AuthServiceClient:
    http_client: HttpClient

    def __init__(self,
                 *,
                 httpx_client: httpx.AsyncClient,
                 auth_tokens_processor: AuthTokensProcessor) -> None:
        self.http_client = AuthenticatedHttpClient(
            httpx_client=httpx_client,
            base_url=settings.auth.api_v1_url,
            auth_tokens_processor=auth_tokens_processor,
        )

    async def get_user(self, *, user_id: uuid.UUID) -> User | None:
        try:
            response = await self.http_client.get(
                settings.auth.get_user_url(user_id=user_id),
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == status.HTTP_404_NOT_FOUND:
                return None

            raise

        return User.model_validate(response.json())

    async def get_users_list(self,
                             *,
                             user_id: uuid.UUID | None = None,
                             user_created: datetime.datetime | None = None,
                             page_size: int | None = None) -> list[User]:
        users_list_params = UsersListParams(
            user_id=user_id,
            user_created=user_created,
            page_size=page_size,
        )

        response = await self.http_client.get(
            settings.auth.get_users_list_url(),
            params=users_list_params.serialize(),
        )

        return [User.model_validate(user_data) for user_data in response.json()]


class AuthenticatedHttpClient(HttpClient):
    auth_tokens_processor: AuthTokensProcessor

    def __init__(self, *, auth_tokens_processor: AuthTokensProcessor, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.auth_tokens_processor = auth_tokens_processor

    async def send_request(self,
                           method: str,
                           url: str,
                           *,
                           headers: dict | None = None,
                           **kwargs: Any) -> HttpResponse:
        auth_tokens = await self.auth_tokens_processor.login()

        try:
            return await self._send_authenticated_request(
                method,
                url,
                headers=headers,
                auth_tokens=auth_tokens,
                **kwargs,
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == status.HTTP_401_UNAUTHORIZED:
                auth_tokens = await self.auth_tokens_processor.refresh()

                return await self._send_authenticated_request(
                    method,
                    url,
                    headers=headers,
                    auth_tokens=auth_tokens,
                    **kwargs,
                )

            else:
                raise

    async def _send_authenticated_request(self,
                                          method: str,
                                          url: str,
                                          *,
                                          headers: dict | None = None,
                                          auth_tokens: AuthTokens,
                                          **kwargs: Any) -> HttpResponse:
        token_headers: dict = {
            'Authorization': f'Bearer {auth_tokens.access_token}',
        }

        return await super().send_request(
            method,
            url,
            headers={
                **token_headers,
                **(headers or {}),
            },
            **kwargs,
        )


async def get_auth_service_client(httpx_client: HTTPXClientTaskiqDep,
                                  auth_tokens_processor: AuthTokensProcessorTaskiqDep) -> AuthServiceClient:
    return AuthServiceClient(
        httpx_client=httpx_client,
        auth_tokens_processor=auth_tokens_processor,
    )


AuthServiceClientTaskiqDep = Annotated[AuthServiceClient, TaskiqDepends(get_auth_service_client)]
