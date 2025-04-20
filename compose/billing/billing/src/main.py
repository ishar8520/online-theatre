from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from httpx import AsyncClient

from src.api.v1.endpoints import admin, payment


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[dict[str, AsyncClient], None]:
    """
    Контекстный менеджер жизненного цикла приложения.

    При старте создаёт асинхронный HTTPX-клиент и передаёт его в состояние приложения,
    а при завершении автоматически закрывает клиент.

    :param _app: экземпляр FastAPI-приложения
    :yield: словарь с ключом 'httpx_client' для доступа к AsyncClient
    """
    async with (
        httpx.AsyncClient() as httpx_client,
    ):
        yield {
            'httpx_client': httpx_client,
        }


base_api_prefix = '/billing/api'
app = FastAPI(
    lifespan=lifespan,
    title='Billing service',
    description='Service for purchase subscribe, movies and emoji',
    docs_url=f'{base_api_prefix}/openapi',
    openapi_url=f'{base_api_prefix}/openapi.json',
    default_response_class=JSONResponse,
)


@app.get(f'{base_api_prefix}/_health')
async def healthcheck() -> dict[str, Any]:
    """
    Эндпоинт проверки работоспособности сервиса.

    :return: Пустой JSON-объект в случае доступности сервиса
    """
    return {}


billing_api_prefix = f'{base_api_prefix}/v1'

app.include_router(
    payment.router,
    prefix=f'{billing_api_prefix}/payment',
    tags=['payment']
)
app.include_router(
    admin.router,
    prefix=f'{billing_api_prefix}/admin',
    tags=['admin_payment']
)
