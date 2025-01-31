from __future__ import annotations

from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.oauth2 import BaseOAuth2

from .base import OAuthClientFactory
from ......core import settings


class GoogleOAuthClientFactory(OAuthClientFactory):
    def create(self) -> BaseOAuth2:
        return GoogleOAuth2(
            client_id=settings.oauth.google_client_id,
            client_secret=settings.oauth.google_client_secret,
        )
