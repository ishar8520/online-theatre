from fastapi import Depends, Request
from redis.asyncio import Redis
from services.shortener import ShortenerService


async def get_redis(request: Request) -> Redis:
    return request.app.state.redis


def get_shortener_service(redis=Depends(get_redis)) -> ShortenerService:
    return ShortenerService(redis)
