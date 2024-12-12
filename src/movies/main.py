from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from contextlib import asynccontextmanager

from .api.v1.endpoints import films, genres, persons
from .core import config
from .db import elastic, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    elastic.es = AsyncElasticsearch(hosts=[f'http://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])
    try:
        yield
    finally:
        await redis.redis.close()
        await elastic.es.close()


app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=JSONResponse,
    lifespan=lifespan
)


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
