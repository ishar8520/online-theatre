from __future__ import annotations

from typing import Annotated

import httpx
from fastapi import Depends, Request


async def get_httpx_client(request: Request) -> httpx.AsyncClient:
    """
    Возвращает асинхронный HTTPX-клиент, сохранённый в состоянии запроса.

    :param request: экземпляр FastAPI Request с атрибутом state.httpx_client
    :return: экземпляр AsyncClient для выполнения HTTP-запросов
    """
    client: httpx.AsyncClient = request.state.httpx_client
    return client


HTTPXClientDep = Annotated[httpx.AsyncClient, Depends(get_httpx_client)]
