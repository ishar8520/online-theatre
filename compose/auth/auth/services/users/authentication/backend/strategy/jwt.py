from __future__ import annotations

import jwt

from .base import (
    Strategy,
    StrategyDestroyNotSupportedError,
    InvalidToken,
)
from .... import exceptions
from ....jwt import (
    SecretType,
    decode_jwt,
    generate_jwt,
)
from ....manager import UserManager
from .....cache import (
    AbstractCache,
    AbstractCacheService,
)
from ......models.sqlalchemy import User


class JWTStrategyDestroyNotSupportedError(StrategyDestroyNotSupportedError):
    def __init__(self) -> None:
        message = "A JWT can't be invalidated: it's valid until it expires."
        super().__init__(message)


class JWTStrategy(Strategy):
    secret: SecretType
    lifetime_seconds: int | None
    token_audience: list[str]
    algorithm: str
    public_key: SecretType | None

    cache: AbstractCache

    def __init__(self,
                 *,
                 secret: SecretType,
                 lifetime_seconds: int | None = None,
                 token_audience: list[str] | None = None,
                 algorithm: str = 'HS256',
                 public_key: SecretType | None = None,
                 cache_service: AbstractCacheService) -> None:
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds

        if token_audience is None:
            token_audience = ['users:auth']

        self.token_audience = token_audience
        self.algorithm = algorithm
        self.public_key = public_key

        self.cache = cache_service.get_cache(key_prefix='jwt')

    @property
    def encode_key(self) -> SecretType:
        return self.secret

    @property
    def decode_key(self) -> SecretType:
        return self.public_key or self.secret

    async def read_token(self, token: str, user_manager: UserManager) -> User | None:
        try:
            data = decode_jwt(
                token,
                secret=self.decode_key,
                audience=self.token_audience,
                algorithms=[self.algorithm],
            )
        except jwt.PyJWTError:
            return None

        user_id = data.get('sub')
        if user_id is None:
            return None

        try:
            parsed_id = user_manager.parse_id(user_id)
        except exceptions.InvalidID:
            return None

        try:
            user = await user_manager.get(parsed_id)
        except exceptions.UserDoesNotExist:
            return None

        try:
            await self._validate_token(token=token, user=user)
        except InvalidToken:
            return None

        return user

    async def _validate_token(self, token: str, user: User) -> None:
        pass

    async def write_token(self, user: User) -> str:
        data = {
            'sub': str(user.id),
            'aud': self.token_audience,
        }

        token = generate_jwt(
            data,
            secret=self.encode_key,
            lifetime_seconds=self.lifetime_seconds,
            algorithm=self.algorithm,
        )
        await self._save_token(token=token, user=user)

        return token

    async def _save_token(self, token: str, user: User) -> None:
        pass

    async def destroy_token(self, token: str, user: User) -> None:
        raise JWTStrategyDestroyNotSupportedError()


class AccessJWTStrategy(JWTStrategy):
    async def _validate_token(self, token: str, user: User) -> None:
        cache_key = self._create_cache_key(token)

        if await self.cache.get(cache_key) is not None:
            raise InvalidToken

    async def destroy_token(self, token: str, user: User) -> None:
        cache_key = self._create_cache_key(token)
        await self.cache.set(cache_key, 'access', timeout=self.lifetime_seconds)

    def _create_cache_key(self, token: str) -> str:
        return f'access-{token}'


class RefreshJWTStrategy(JWTStrategy):
    async def _validate_token(self, token: str, user: User) -> None:
        cache_key = self._create_cache_key(token)

        if await self.cache.get(cache_key) is None:
            raise InvalidToken

        await self.destroy_token(token=token, user=user)

    async def _save_token(self, token: str, user: User) -> None:
        cache_key = self._create_cache_key(token)
        await self.cache.set(cache_key, 'refresh', timeout=self.lifetime_seconds)

    async def destroy_token(self, token: str, user: User) -> None:
        cache_key = self._create_cache_key(token)
        await self.cache.delete(cache_key)

    def _create_cache_key(self, token: str) -> str:
        return f'refresh-{token}'
