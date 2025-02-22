from __future__ import annotations

from kafka import KafkaConsumer

from ..core.config import settings


class KafkaConsumerService:
    _consumer: KafkaConsumer

    def __init__(self, ):
        topics = ['click']
        self._consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=settings.kafka.hosts,
            auto_offset_reset='earliest',
            group_id='echo-messages-to-stdout',
        )

    def poll(self):
        return self._consumer.poll(timeout_ms=100)
