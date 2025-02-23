from __future__ import annotations

from kafka import KafkaConsumer

from .kafka_topics import KafkaTopicEnum
from ..core.config import settings


class KafkaConsumerService:
    _consumer: KafkaConsumer

    def __init__(self, ):
        topics = [
            KafkaTopicEnum.CLICK.value,
            KafkaTopicEnum.PAGE_VIEW.value,
            KafkaTopicEnum.CUSTOM_EVENT.value,
        ]

        self._consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=settings.kafka.host,
            auto_offset_reset='earliest',
            group_id='echo-messages-to-stdout',
            enable_auto_commit=False,
        )

    def poll(self):
        return self._consumer.poll(timeout_ms=1000)

    def commit(self):
        self._consumer.commit()
