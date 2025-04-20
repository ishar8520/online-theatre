from __future__ import annotations

from fastapi.responses import JSONResponse
import httpx
from src.api.v1.endpoints import admin, payment
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_app) -> AsyncGenerator[dict]:

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
async def healthcheck():
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
