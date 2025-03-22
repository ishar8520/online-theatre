from __future__ import annotations

import logging.config

import taskiq_fastapi
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from .core import settings, LOGGING

logging.config.dictConfig(LOGGING)

broker = AioPikaBroker(
    url=settings.rabbitmq.url,
).with_result_backend(RedisAsyncResultBackend(
    redis_url=settings.redis.url,
))
taskiq_fastapi.init(broker, 'notifications_queue.main:app')
