from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime

from .exceptions import InvalidTransformData, UnknownTransformerType


class TransformerFactory():
    @staticmethod
    def get(event_name: str, data: str):
        if event_name == ClickEventTransformer.get_type():
            return ClickEventTransformer(data=data)

        raise UnknownTransformerType


class AbstractEventTransformer(ABC):
    _data_dict: dict

    def __init__(self, data: str):
        try:
            self._data_dict = json.loads(data)
        except json.JSONDecodeError:
            raise InvalidTransformData

    @abstractmethod
    def transform(self) -> dict: ...

    @staticmethod
    @abstractmethod
    def get_type() -> str: ...


class ClickEventTransformer(AbstractEventTransformer):
    def transform(self) -> dict:
        return {
            'user_id': self._data_dict['user_id'],
            'element': self._data_dict['element'],
            'timestamp': datetime.fromisoformat(self._data_dict['timestamp']),
        }

    @staticmethod
    def get_type() -> str:
        return 'click'


class PageViewEventTransformer(AbstractEventTransformer):
    def transform(self) -> dict:
        return {
            'user_id': self._data_dict['user_id'],
            'url': self._data_dict['url'],
            'duration': self._data_dict['duration'],
            'timestamp': datetime.fromisoformat(self._data_dict['timestamp']),
        }

    @staticmethod
    def get_type() -> str:
        return 'page_view'


class CustomEventTransformer(AbstractEventTransformer):
    def transform(self) -> dict:
        return {
            'user_id': self._data_dict['user_id'],
            'event_type': self._data_dict['event_type'],
            'movie_quality': self._data_dict['movie_quality'],
            'movie_id': self._data_dict['movie_id'],
            'filters': self._data_dict['filters'],
            'timestamp': datetime.fromisoformat(self._data_dict['timestamp']),
        }

    @staticmethod
    def get_type() -> str:
        return 'custom'
