from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from .api.v1.endpoints import films, genres, persons
from .core.config import settings
from .db import elastic, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis.host, port=settings.redis.port)
    elastic.es = AsyncElasticsearch(hosts=[f'http://{settings.elasticsearch.host}:{settings.elasticsearch.port}'])
    try:
        yield
    finally:
        await redis.redis.close()
        await elastic.es.close()


app = FastAPI(
    title=settings.project.name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=JSONResponse,
    lifespan=lifespan
)


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
