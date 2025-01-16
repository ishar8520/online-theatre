from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

from .db import (
    User,
    UserDatabaseDep,
)
from .fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    models,
)
from .fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from ...core import settings


class UserManager(BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.auth.secret_key


async def get_user_manager(user_db: UserDatabaseDep) -> AsyncGenerator[UserManager]:
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl='v1/jwt/login')


def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(
        secret=settings.auth.secret_key,
        lifetime_seconds=settings.auth.jwt_lifetime,
    )


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
fast_api_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager=get_user_manager,
    auth_backends=[auth_backend],
)
