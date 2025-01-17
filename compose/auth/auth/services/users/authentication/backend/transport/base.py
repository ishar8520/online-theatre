from __future__ import annotations

from typing import Protocol

from fastapi import Response
from fastapi.security.base import SecurityBase


class TransportLogoutNotSupportedError(Exception):
    pass


class Transport(Protocol):
    scheme: SecurityBase

    async def get_login_response(self, token: str) -> Response: ...

    async def get_logout_response(self) -> Response: ...
