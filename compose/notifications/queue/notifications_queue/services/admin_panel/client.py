from __future__ import annotations

import uuid
from typing import Annotated

import httpx
from fastapi import (
    status,
)
from taskiq import TaskiqDepends

from .models import (
    Template,
)
from ..auth import (
    AuthenticatedHttpClient,
    AuthTokensProcessor,
    AuthTokensProcessorTaskiqDep,
)
from ..http import HttpClient
from ...core import settings
from ...dependencies.tasks import HTTPXClientTaskiqDep


class AdminPanelServiceClient:
    http_client: HttpClient

    def __init__(self,
                 *,
                 httpx_client: httpx.AsyncClient,
                 auth_tokens_processor: AuthTokensProcessor) -> None:
        self.http_client = AuthenticatedHttpClient(
            httpx_client=httpx_client,
            base_url=settings.notifications_admin_panel.api_v1_url,
            auth_tokens_processor=auth_tokens_processor,
        )

    async def get_template_by_id(self, *, template_id: uuid.UUID) -> Template | None:
        try:
            response = await self.http_client.get(
                settings.notifications_admin_panel.get_template_by_id_url(template_id=template_id),
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == status.HTTP_404_NOT_FOUND:
                return None

            raise

        return Template.model_validate(response.json())

    async def get_template_by_code(self, *, template_code: str) -> Template | None:
        try:
            response = await self.http_client.get(
                settings.notifications_admin_panel.get_template_by_code_url(template_code=template_code),
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == status.HTTP_404_NOT_FOUND:
                return None

            raise

        return Template.model_validate(response.json())


async def get_admin_panel_service_client(
        httpx_client: HTTPXClientTaskiqDep,
        auth_tokens_processor: AuthTokensProcessorTaskiqDep) -> AdminPanelServiceClient:
    return AdminPanelServiceClient(
        httpx_client=httpx_client,
        auth_tokens_processor=auth_tokens_processor,
    )


AdminPanelServiceClientTaskiqDep = Annotated[
    AdminPanelServiceClient,
    TaskiqDepends(get_admin_panel_service_client),
]
