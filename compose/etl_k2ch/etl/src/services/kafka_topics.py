from __future__ import annotations

from enum import Enum


class KafkaTopicEnum(str, Enum):
    CLICK = 'click'
    PAGE_VIEW = 'page_view'
    CUSTOM_EVENT = 'custom_event'
