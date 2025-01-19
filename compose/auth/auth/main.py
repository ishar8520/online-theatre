from __future__ import annotations

import logging.config
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI

from .api.v1.endpoints import (
    roles,
    permissions
)
from .api.v1.endpoints.users import (
    auth,
    register,
    users,
)
from .core import settings, LOGGING
from .db.sqlalchemy import create_db

logging.config.dictConfig(LOGGING)


# noinspection PyUnusedLocal,PyShadowingNames
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict]:
    async with (
        redis.Redis(host=settings.redis.host, port=settings.redis.port) as redis_client,
    ):
        await create_db()
        yield {
            'redis_client': redis_client,
        }


base_api_prefix = '/auth/api'
app = FastAPI(
    title='Auth service',
    description='Authentication & authorization service.',
    docs_url=f'{base_api_prefix}/openapi',
    openapi_url=f'{base_api_prefix}/openapi.json',
    lifespan=lifespan,
)

auth_api_prefix = f'{base_api_prefix}/v1'

app.include_router(
    auth.router,
    prefix=f'{auth_api_prefix}/jwt',
    tags=['auth'],
)
app.include_router(
    register.router,
    prefix=auth_api_prefix,
    tags=['register'],
)
app.include_router(
    users.router,
    prefix=f'{auth_api_prefix}/users',
    tags=['users'],
)
app.include_router(
    roles.router,
    prefix=f'{auth_api_prefix}/roles',
    tags=['roles']
)
app.include_router(
    permissions.router,
    prefix=f'{auth_api_prefix}/permissions',
    tags=['permissions']
)
