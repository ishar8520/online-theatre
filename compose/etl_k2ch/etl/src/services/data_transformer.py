from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime

from .exceptions import InvalidTransformData, UnknownTransformerType
from .kafka_topics import KafkaTopicEnum


class TransformerFactory():
    @staticmethod
    def get(event_name: str):
        if event_name == ClickEventTransformer.get_type():
            return ClickEventTransformer()
        elif event_name == PageViewEventTransformer.get_type():
            return PageViewEventTransformer()
        elif event_name == CustomEventTransformer.get_type():
            return CustomEventTransformer()

        raise UnknownTransformerType


class AbstractEventTransformer(ABC):
    @staticmethod
    @abstractmethod
    def transform(data: list) -> dict: ...

    @staticmethod
    @abstractmethod
    def get_type() -> str: ...


class ClickEventTransformer(AbstractEventTransformer):
    @staticmethod
    def transform(data: dict) -> dict:
        return {
            'user_id': data['user_id'],
            'element': data['element'],
            'timestamp': datetime.fromisoformat(data['timestamp']),
        }

    @staticmethod
    def get_type() -> str:
        return KafkaTopicEnum.CLICK.value


class PageViewEventTransformer(AbstractEventTransformer):
    @staticmethod
    def transform(data: dict) -> dict:
        return {
            'user_id': data['user_id'],
            'url': data['url'],
            'duration': str(data['duration']),
            'timestamp': datetime.fromisoformat(data['timestamp']),
        }

    @staticmethod
    def get_type() -> str:
        return KafkaTopicEnum.PAGE_VIEW.value


class CustomEventTransformer(AbstractEventTransformer):
    @staticmethod
    def transform(data: dict) -> dict:
        return {
            'user_id': data['user_id'],
            'event_type': data['event_type'],
            'movie_quality': data['movie_quality'],
            'movie_id': data['movie_id'],
            'filters': data['filters'],
            'timestamp': datetime.fromisoformat(data['timestamp']),
        }

    @staticmethod
    def get_type() -> str:
        return KafkaTopicEnum.CUSTOM_EVENT.value
