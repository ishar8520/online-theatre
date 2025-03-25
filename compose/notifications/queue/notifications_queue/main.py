from __future__ import annotations

import logging.config
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from .api.v1.endpoints import notifications
from .broker import BROKERS
from .core import LOGGING

logging.config.dictConfig(LOGGING)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    async with (
        httpx.AsyncClient() as httpx_client,
    ):
        _app.state.httpx_client = httpx_client

        for _broker in BROKERS.values():
            if not _broker.is_worker_process:
                await _broker.startup()

        yield

        for _broker in BROKERS.values():
            if not _broker.is_worker_process:
                await _broker.shutdown()


base_api_prefix = '/api'
app = FastAPI(
    title='Notifications queue service',
    description='API for queueing notifications.',
    docs_url=f'{base_api_prefix}/openapi',
    openapi_url=f'{base_api_prefix}/openapi.json',
    lifespan=lifespan,
)


@app.get(f'{base_api_prefix}/_health')
async def healthcheck() -> dict:
    return {}


ugc_api_prefix = f'{base_api_prefix}/v1'

app.include_router(
    notifications.router,
    prefix=f'{ugc_api_prefix}/notifications',
    tags=['notifications'],
)
