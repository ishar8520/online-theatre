from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.oauth2 import BaseOAuth2

from ....core import settings


async def get_google_oauth_client() -> BaseOAuth2:
    return GoogleOAuth2(
        client_id=settings.oauth.google_client_id,
        client_secret=settings.oauth.google_client_secret,
    )


GoogleOAuthClientDep = Annotated[BaseOAuth2, Depends(get_google_oauth_client)]
