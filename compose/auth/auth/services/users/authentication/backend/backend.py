from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Response, status

from .strategy import (
    Strategy,
    StrategyDep,
    StrategyDestroyNotSupportedError,
)
from .transport import (
    Transport,
    TransportDep,
    TransportLogoutNotSupportedError,
)
from ...manager import UserManager
from .....models.sqlalchemy import User


class AuthenticationBackend:
    """
    Combination of an authentication transport and strategy.

    Together, they provide a full authentication method logic.

    :param name: Name of the backend.
    :param transport: Authentication transport instance.
    :param strategy: An authentication strategy instance.
    """

    name: str
    transport: Transport

    def __init__(
            self,
            name: str,
            transport: Transport,
            strategy: Strategy,
    ):
        self.name = name
        self.transport = transport
        self.strategy = strategy

    async def authenticate(self, token: str, user_manager: UserManager) -> User | None:
        return await self.strategy.read_token(token, user_manager)

    async def login(self, user: User) -> Response:
        token = await self.strategy.write_token(user)
        return await self.transport.get_login_response(token)

    async def logout(self, user: User, token: str) -> Response:
        try:
            await self.strategy.destroy_token(token, user)
        except StrategyDestroyNotSupportedError:
            pass

        try:
            response = await self.transport.get_logout_response()
        except TransportLogoutNotSupportedError:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)

        return response


async def get_authentication_backend(transport: TransportDep,
                                     strategy: StrategyDep) -> AuthenticationBackend:
    return AuthenticationBackend(
        name='jwt',
        transport=transport,
        strategy=strategy,
    )


AuthenticationBackendDep = Annotated[AuthenticationBackend, Depends(get_authentication_backend)]
