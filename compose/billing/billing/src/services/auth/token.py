from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=settings.auth.oauth2_token_url,
    auto_error=False,
)
OAuth2TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_token(token: OAuth2TokenDep) -> str:
    """
    Извлекает OAuth2 токен из зависимости FastAPI.

    :param token: строка токена, полученная через OAuth2PasswordBearer
    :return: тот же токен для передачи дальше в зависимостях
    """
    return token


TokenDep = Annotated[str, Depends(get_token)]
