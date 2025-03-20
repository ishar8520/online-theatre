from contextlib import asynccontextmanager

from api import router
from config import REDIS_URL
from fastapi import FastAPI
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis.from_url(REDIS_URL, decode_responses=True)
    yield
    await app.state.redis.close()


app = FastAPI(lifespan=lifespan)


app.include_router(router)
