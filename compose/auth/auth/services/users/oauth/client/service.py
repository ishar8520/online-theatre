from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated

from fastapi import Depends
from httpx_oauth.oauth2 import BaseOAuth2

from .factories import (
    OAuthClientFactory,
    GoogleOAuthClientFactory,
    FakeGoogleOAuthClientFactory,
)
from .....core import settings


class OAuthClientService:
    client_factories: Mapping[str, OAuthClientFactory]

    def __init__(self, *, client_factories: Mapping[str, OAuthClientFactory]) -> None:
        self.client_factories = client_factories

    def create_client(self, provider_name: str) -> BaseOAuth2 | None:
        client_factory = self.client_factories.get(provider_name)

        if client_factory is None:
            return None

        return client_factory.create()


async def get_oauth_client_service() -> OAuthClientService:
    client_factories: Mapping[str, OAuthClientFactory]

    if settings.test_mode:
        client_factories = {
            'google': FakeGoogleOAuthClientFactory(),
        }
    else:
        client_factories = {
            'google': GoogleOAuthClientFactory(),
        }

    return OAuthClientService(client_factories=client_factories)


OAuthClientServiceDep = Annotated[OAuthClientService, Depends(get_oauth_client_service)]
