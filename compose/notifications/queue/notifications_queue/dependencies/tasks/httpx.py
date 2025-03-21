from __future__ import annotations

from typing import Annotated

import httpx
from taskiq import TaskiqDepends

from .common import RequestTaskiqDep


async def get_httpx_client(request: RequestTaskiqDep) -> httpx.AsyncClient:
    return request.app.state.httpx_client


HTTPXClientTaskiqDep = Annotated[httpx.AsyncClient, TaskiqDepends(get_httpx_client)]
