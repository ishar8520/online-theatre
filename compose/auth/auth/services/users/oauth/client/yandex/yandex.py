from __future__ import annotations

from enum import Enum
from typing import Any, cast, Optional

from httpx_oauth.exceptions import GetProfileError, GetIdEmailError
from httpx_oauth.oauth2 import BaseOAuth2


class AuthEndpointsEnum(str, Enum):
    AUTHORIZE = "https://oauth.yandex.ru/authorize"
    ACCESS_TOKEN = "https://oauth.yandex.ru/token"
    REVOKE_TOKEN = "https://oauth.yandex.ru/revoke_token"
    PROFILE = "https://login.yandex.ru/info"


class YandexOAuth2(BaseOAuth2):

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            name: str = 'yandex'
    ):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            name=name,
            base_scopes=[
                AuthEndpointsEnum.PROFILE.value
            ],
            authorize_endpoint=AuthEndpointsEnum.AUTHORIZE.value,
            access_token_endpoint=AuthEndpointsEnum.ACCESS_TOKEN.value,
            revoke_token_endpoint=AuthEndpointsEnum.REVOKE_TOKEN.value,
            token_endpoint_auth_method="client_secret_post",
            revocation_endpoint_auth_method="client_secret_post",
        )

    async def get_profile(self, token: str) -> dict[str, Any]:
        async with self.get_httpx_client() as client:
            response = await client.get(
                AuthEndpointsEnum.PROFILE.value,
                headers={**self.request_headers, "Authorization": f"OAuth {token}"},
            )

            if response.status_code >= 400:
                raise GetProfileError(response=response)

            return cast(dict[str, Any], response.json())

    async def get_id_email(self, token: str) -> tuple[str, Optional[str]]:
        try:
            profile = await self.get_profile(token)
        except GetProfileError as e:
            raise GetIdEmailError(response=e.response)

        user_id = profile["id"]
        user_email = profile["default_email"]

        return user_id, user_email
