from __future__ import annotations

import abc

from httpx_oauth.oauth2 import BaseOAuth2


class OAuthClientFactory(abc.ABC):
    @abc.abstractmethod
    def create(self) -> BaseOAuth2: ...
