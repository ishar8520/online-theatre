from __future__ import annotations

import logging.config
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core import LOGGING
from .db.sqlalchemy import create_db_tables
from .services.users import routers as users_routers

logging.config.dictConfig(LOGGING)


# noinspection PyUnusedLocal,PyShadowingNames
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    await create_db_tables()
    yield


auth_api_prefix = '/auth/api'
app = FastAPI(
    title='Auth service',
    description='Authentication & authorization service.',
    docs_url=f'{auth_api_prefix}/openapi',
    openapi_url=f'{auth_api_prefix}/openapi.json',
    lifespan=lifespan,
)

app.include_router(
    users_routers.auth_router,
    prefix=f'{auth_api_prefix}/jwt',
    tags=['auth'],
)
app.include_router(
    users_routers.register_router,
    prefix=auth_api_prefix,
    tags=['auth'],
)
app.include_router(
    users_routers.reset_password_router,
    prefix=auth_api_prefix,
    tags=['auth'],
)
app.include_router(
    users_routers.verify_router,
    prefix=auth_api_prefix,
    tags=['auth'],
)
app.include_router(
    users_routers.users_router,
    prefix=f'{auth_api_prefix}/users',
    tags=['users'],
)
