from __future__ import annotations

from typing import Generic, Optional

import jwt

from .base import (
    Strategy,
    StrategyDestroyNotSupportedError,
)
from ... import exceptions
from ...jwt import SecretType, decode_jwt, generate_jwt
from ...manager import BaseUserManager
from ...models import UP, ID


class JWTStrategyDestroyNotSupportedError(StrategyDestroyNotSupportedError):
    def __init__(self) -> None:
        message = "A JWT can't be invalidated: it's valid until it expires."
        super().__init__(message)


class JWTStrategy(Strategy[UP, ID], Generic[UP, ID]):
    def __init__(
            self,
            secret: SecretType,
            lifetime_seconds: Optional[int],
            token_audience: list[str] | None = None,
            algorithm: str = "HS256",
            public_key: Optional[SecretType] = None,
    ):
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds

        if token_audience is None:
            token_audience = ['fastapi-users:auth']

        self.token_audience = token_audience
        self.algorithm = algorithm
        self.public_key = public_key

    @property
    def encode_key(self) -> SecretType:
        return self.secret

    @property
    def decode_key(self) -> SecretType:
        return self.public_key or self.secret

    async def read_token(
            self, token: Optional[str], user_manager: BaseUserManager[UP, ID]
    ) -> Optional[UP]:
        if token is None:
            return None

        try:
            data = decode_jwt(
                token, self.decode_key, self.token_audience, algorithms=[self.algorithm]
            )
            user_id = data.get("sub")
            if user_id is None:
                return None
        except jwt.PyJWTError:
            return None

        try:
            parsed_id = user_manager.parse_id(user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def write_token(self, user: UP) -> str:
        data = {"sub": str(user.id), "aud": self.token_audience}
        return generate_jwt(
            data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm
        )

    async def destroy_token(self, token: str, user: UP) -> None:
        raise JWTStrategyDestroyNotSupportedError()
