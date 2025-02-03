from __future__ import annotations

from typing import Type

from httpx_oauth.oauth2 import BaseOAuth2

from .base import BaseOAuthClientFactory
from ..yandex.yandex import YandexOAuth2
from ......core import settings


class YandexOAuthClientFactory(BaseOAuthClientFactory):
    def get_client_class(self) -> Type[BaseOAuth2]:
        return YandexOAuth2

    def get_client_kwargs(self) -> dict:
        return {
            'client_id': settings.oauth.yandex_client_id,
            'client_secret': settings.oauth.yandex_client_secret,
        }
