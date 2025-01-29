from __future__ import annotations

from typing import Annotated

import httpx

from fastapi.params import Depends
from json import JSONDecodeError

from .exceptions import (
    ResponseJsonError,
    RequestError
)
from ..token import TokenDep


class HttpAsync:
    _token: str

    def __init__(self, token: str):
        self._token = token

    async def get(self, url: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url=url,
                    headers=self._get_headers()
                )
                return response.json()
        except JSONDecodeError:
            raise ResponseJsonError()
        except httpx.RequestError:
            raise RequestError

    async def post(self, url: str, json: dict) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=url,
                    headers=self._get_headers(),
                    json=json
                )
                return response.json()
        except JSONDecodeError:
            raise ResponseJsonError()
        except httpx.RequestError:
            raise RequestError

    def _get_headers(self):
        return {
            'Authorization': f"Bearer {self._token}"
        }


def get_http_async_client(token: TokenDep):
    return HttpAsync(token)


HttpAsyncDep = Annotated[HttpAsync, Depends(get_http_async_client)]
