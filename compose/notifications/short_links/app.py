from contextlib import asynccontextmanager

from api import router
from config import settings
from fastapi import FastAPI
from redis.asyncio import Redis

REDIS_URL = f'redis://{settings.redis.host}:{settings.redis.port}'
base_api_prefix = '/short_link/api'


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis.from_url(REDIS_URL, decode_responses=True)
    yield
    await app.state.redis.close()


app = FastAPI(
    docs_url=f'{base_api_prefix}/openapi',
    openapi_url=f'{base_api_prefix}/openapi.json',
    lifespan=lifespan
)


app.include_router(router)
