import logging
from abc import ABC, abstractmethod

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from core.config import settings
from models.event import EventContainer

logger = logging.getLogger(__name__)


class EventRepoBaseError(Exception):
    """Базовая ошибка репозитория событий."""


class EventRepoConnectionError(Exception):
    """Ошибка соединения репозитория событий."""


class BaseEventRepo(ABC):
    """Абстрактный базовый класс для репозитория аналитических событий."""

    @abstractmethod
    async def send_event(self, event: EventContainer) -> None:
        """Метод для отправки события в хранилище/брокер."""


class KafkaEventRepo(BaseEventRepo):
    """Репозиторий событий использующий Kafka в качестве брокера."""

    def __init__(self, kafka_hosts: str) -> None:
        self.kafka_hosts = kafka_hosts
        self.kafka_producer = None

    async def start(self):
        """Запускаем продюсер."""
        self.kafka_producer = AIOKafkaProducer(bootstrap_servers=self.kafka_hosts)
        await self.kafka_producer.start()

    async def stop(self):
        """Останавливаем продюсер."""
        if self.kafka_producer:
            await self.kafka_producer.stop()

    async def send_event(self, event: EventContainer, topic: str) -> None:
        """Метод для отправки события в хранилище/брокер."""
        message = event.model_dump_json()
        try:
            await self.kafka_producer.send_and_wait(
                topic=topic, value=message.encode()
            )
        except KafkaError as e:
            logger.exception(
                f"Произошла ошибка при отправке сообщения в Kafka {message=}"
            )
            raise EventRepoConnectionError from e


def get_kafka_event_repo() -> KafkaEventRepo:
    return KafkaEventRepo(kafka_hosts=settings.kafka_hosts_as_list)
