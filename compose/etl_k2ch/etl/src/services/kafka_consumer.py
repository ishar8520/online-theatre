from __future__ import annotations

from kafka import KafkaConsumer

from .kafka_topics import KafkaTopicEnum
from ..core.config import settings


class KafkaConsumerService:
    _consumer: KafkaConsumer

    def __init__(self, topic: str):

        self._consumer = KafkaConsumer(
            topic,
            bootstrap_servers=settings.kafka.host,
            auto_offset_reset='earliest',
            group_id='echo-messages-to-stdout',
            enable_auto_commit=False,
            max_poll_records=100
        )

    def poll(self):
        return self._consumer.poll(timeout_ms=1000)

    def commit(self):
        self._consumer.commit()
