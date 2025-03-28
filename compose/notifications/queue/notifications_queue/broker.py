from __future__ import annotations

import logging.config

import taskiq_fastapi
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from .core import settings, LOGGING

logging.config.dictConfig(LOGGING)


def create_broker(*, queue_name: str | None = None) -> AioPikaBroker:
    broker_kwargs: dict = {
        'declare_exchange_kwargs': {
            'durable': True,
        },
        'declare_queues_kwargs': {
            'durable': True,
        },
    }

    if queue_name:
        broker_kwargs.update({
            'exchange_name': queue_name,
            'queue_name': queue_name,
        })

    _broker = AioPikaBroker(
        url=settings.rabbitmq.url,
        **broker_kwargs,
    ).with_result_backend(RedisAsyncResultBackend(
        redis_url=settings.redis.url,
    ))
    taskiq_fastapi.init(_broker, 'notifications_queue.main:app')

    return _broker


broker = create_broker()
undelivered_messages_broker = create_broker(queue_name='undelivered_messages')

BROKERS = {
    'default': broker,
    'undelivered_messages': undelivered_messages_broker,
}
