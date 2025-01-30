from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from httpx_oauth.oauth2 import BaseOAuth2

from .google import GoogleOAuthClientDep


async def get_oauth_client(google_oauth_client: GoogleOAuthClientDep) -> BaseOAuth2:
    return google_oauth_client


OAuthClientDep = Annotated[BaseOAuth2, Depends(get_oauth_client)]
