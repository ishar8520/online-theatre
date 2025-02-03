from __future__ import annotations

import time
from typing import Type, Any

import httpx
from httpx_oauth.oauth2 import (
    BaseOAuth2,
    OAuth2Token,
    RefreshTokenNotSupportedError,
    OAuth2RequestError
)

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


class FakeYandexOAuth2(YandexOAuth2):
    async def get_access_token(self,
                               code: str,
                               redirect_uri: str,
                               code_verifier: str | None = None) -> OAuth2Token:
        return OAuth2Token({
            'access_token': 'access_token',
            'expires_in': 3600,
            'token_type': 'Bearer',
            'id_token': 'id_token',
            'expires_at': int(time.time()),
        })

    async def refresh_token(self, refresh_token: str) -> OAuth2Token:
        raise RefreshTokenNotSupportedError

    async def revoke_token(self, token: str, token_type_hint: str | None = None) -> None:
        return None

    async def get_profile(self, token: str) -> dict[str, Any]:
        return {
            'id': '90009206',
            'login': 'test',
            'client_id': 'client_id',
            'display_name': 'test.user',
            'default_email': 'test.user@yandex.ru',
            'emails': ['test.user@yandex.ru'],
        }

    async def send_request(
            self,
            client: httpx.AsyncClient,
            request: httpx.Request,
            auth: httpx.Auth | None,
            *,
            exc_class: type[OAuth2RequestError],
    ) -> httpx.Response:
        return httpx.Response(status_code=200, json={})


class FakeYandexOAuthClientFactory(BaseOAuthClientFactory):
    def get_client_class(self) -> Type[BaseOAuth2]:
        return FakeYandexOAuth2

    def get_client_kwargs(self) -> dict:
        return {
            'client_id': 'client_id',
            'client_secret': 'client_secret',
        }
