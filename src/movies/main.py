from __future__ import annotations

import logging.config
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import elasticsearch
import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .api.v1.endpoints import films, genres, persons
from .core import settings, LOGGING

logging.config.dictConfig(LOGGING)


# noinspection PyUnusedLocal,PyShadowingNames
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict]:
    async with (
        redis.Redis(host=settings.redis.host, port=settings.redis.port) as redis_client,
        elasticsearch.AsyncElasticsearch(settings.elasticsearch.url) as elasticsearch_client,
    ):
        yield {
            'redis_client': redis_client,
            'elasticsearch_client': elasticsearch_client,
        }


app = FastAPI(
    title=settings.project.name,
    description='Backend service that returns films, persons (actors, writers, directors) and genres of films by uuid',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=JSONResponse,
    lifespan=lifespan
)

app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
