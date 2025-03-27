from __future__ import annotations

import abc
import uuid
from typing import Annotated, Any

import httpx
from fastapi import (
    status,
    HTTPException,
)
from taskiq import TaskiqDepends

from .client import (
    AdminPanelServiceClient,
    AdminPanelServiceClientTaskiqDep,
)
from .models import (
    Template,
)


class AbstractAdminPanelService(abc.ABC):
    @abc.abstractmethod
    async def get_template_by_id(self, *, template_id: uuid.UUID) -> Template | None: ...

    @abc.abstractmethod
    async def get_template_by_code(self, *, template_code: str) -> Template | None: ...


class AdminPanelService(AbstractAdminPanelService):
    admin_panel_service_client: AdminPanelServiceClient

    def __init__(self, *, admin_panel_service_client: AdminPanelServiceClient) -> None:
        self.admin_panel_service_client = admin_panel_service_client

    async def get_template_by_id(self, *, template_id: uuid.UUID) -> Template | None:
        return await GetTemplateByIdRequest(
            admin_panel_service_client=self.admin_panel_service_client,
            template_id=template_id,
        ).send_request()

    async def get_template_by_code(self, *, template_code: str) -> Template | None:
        return await GetTemplateByCodeRequest(
            admin_panel_service_client=self.admin_panel_service_client,
            template_code=template_code,
        ).send_request()


class AdminPanelServiceRequest[TResponse](abc.ABC):
    admin_panel_service_client: AdminPanelServiceClient

    def __init__(self, *, admin_panel_service_client: AdminPanelServiceClient) -> None:
        self.admin_panel_service_client = admin_panel_service_client

    async def send_request(self) -> TResponse:
        try:
            return await self._send_request()

        except httpx.HTTPError:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    @abc.abstractmethod
    async def _send_request(self) -> TResponse:
        ...


class GetTemplateByIdRequest(AdminPanelServiceRequest[Template | None]):
    template_id: uuid.UUID

    def __init__(self, *, template_id: uuid.UUID, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.template_id = template_id

    async def _send_request(self) -> Template | None:
        return await self.admin_panel_service_client.get_template_by_id(template_id=self.template_id)


class GetTemplateByCodeRequest(AdminPanelServiceRequest[Template | None]):
    template_code: str

    def __init__(self, *, template_code: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.template_code = template_code

    async def _send_request(self) -> Template | None:
        return await self.admin_panel_service_client.get_template_by_code(template_code=self.template_code)


async def get_admin_panel_service(
        admin_panel_service_client: AdminPanelServiceClientTaskiqDep) -> AbstractAdminPanelService:
    return AdminPanelService(admin_panel_service_client=admin_panel_service_client)


AdminPanelServiceTaskiqDep = Annotated[AbstractAdminPanelService, TaskiqDepends(get_admin_panel_service)]
