from __future__ import annotations

import logging.config
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.v1.endpoints import users
from .api.v1.endpoints import roles
from .core import LOGGING
from .db.sqlalchemy import create_db_tables

logging.config.dictConfig(LOGGING)


# noinspection PyUnusedLocal,PyShadowingNames
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    await create_db_tables()
    yield


base_api_prefix = '/auth/api'
app = FastAPI(
    title='Auth service',
    description='Authentication & authorization service.',
    docs_url=f'{base_api_prefix}/openapi',
    openapi_url=f'{base_api_prefix}/openapi.json',
    lifespan=lifespan,
)

auth_api_prefix = f'{base_api_prefix}/v1'


app.include_router(roles.router, prefix=f'{auth_api_prefix}/roles', tags=['auth'])

app.include_router(
    users.users_routers.auth,
    prefix=f'{auth_api_prefix}/jwt',
    tags=['auth'],
)
app.include_router(
    users.users_routers.register,
    prefix=auth_api_prefix,
    tags=['auth'],
)
app.include_router(
    users.users_routers.reset_password,
    prefix=auth_api_prefix,
    tags=['auth'],
)
app.include_router(
    users.users_routers.verify,
    prefix=auth_api_prefix,
    tags=['auth'],
)
app.include_router(
    users.users_routers.users,
    prefix=f'{auth_api_prefix}/users',
    tags=['users'],
)
