from __future__ import annotations

from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, status

from src.models.auth import User
from src.services.auth.client import AuthClientDep


async def get_auth_user(auth_client: AuthClientDep) -> User:
    """
    Получает информацию о текущем авторизованном пользователе.

    Использует AuthClient для запроса профиля пользователя к сервису аутентификации.

    :param auth_client: экземпляр AuthClient из зависимостей
    :return: объект User при успешном ответе от сервиса
    :raises HTTPException:
        - 401, если нет токена или он недействителен
        - 403, если нет прав доступа
        - 503, если сервис аутентификации недоступен
    """
    try:
        user_data = await auth_client.get_user_profile()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    except httpx.HTTPError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    return User(**user_data)


AuthUserDep = Annotated[User, Depends(get_auth_user)]
