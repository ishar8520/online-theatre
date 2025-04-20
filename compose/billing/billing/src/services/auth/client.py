from __future__ import annotations

from typing import Annotated, Any

import httpx
from fastapi import Depends, HTTPException, status

from src.core.config import settings
from src.dependencies import HTTPXClientDep
from src.models.auth import User
from src.services.auth.token import TokenDep


class AuthClient:
    """
    Клиент для взаимодействия с сервисом аутентификации.

    :param httpx_client: асинхронный HTTPX-клиент для выполнения запросов
    :param token: токен авторизации пользователя
    """

    httpx_client: httpx.AsyncClient
    token: str

    def __init__(self, *, httpx_client: httpx.AsyncClient, token: str) -> None:
        """
        Инициализирует AuthClient.

        :param httpx_client: асинхронный HTTPX-клиент для выполнения запросов
        :param token: токен авторизации пользователя
        """
        self.httpx_client = httpx_client
        self.token = token

    async def get_user_profile(self) -> dict[str, Any]:
        """
        Получает профиль пользователя из сервиса аутентификации.

        :return: словарь с данными пользователя
        :raises HTTPException: при ошибках HTTP-запроса
        """
        response = await self.httpx_client.get(
            url=settings.auth.user_profile_url,
            headers=self.get_headers(),
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return data

    def get_headers(self) -> dict[str, str]:
        """
        Формирует заголовки для запросов к сервису аутентификации.

        :return: словарь заголовков, включая Authorization
        """
        return {
            'X-Request-Id': 'billing',
            'Authorization': f'Bearer {self.token}',
        }


def get_auth_client(httpx_client: HTTPXClientDep, token: TokenDep) -> AuthClient:
    """
    Фабрика для создания экземпляра AuthClient из зависимостей FastAPI.

    :param httpx_client: HTTPX-клиент из зависимостей
    :param token: токен пользователя из зависимостей
    :return: инициализированный AuthClient
    """
    return AuthClient(httpx_client=httpx_client, token=token)


AuthClientDep = Annotated[AuthClient, Depends(get_auth_client)]


async def get_current_admin_user(
    auth_client: AuthClient = Depends(get_auth_client)
) -> User:
    """
    Выполняет проверку авторизации и прав администратора.

    :param auth_client: экземпляр AuthClient для выполнения запросов
    :return: объект User при успешной проверке
    :raises HTTPException: если пользователь не авторизован, нет прав или сервис недоступен
    """
    try:
        user_data = await auth_client.get_user_profile()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещён: недостаточно прав"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не авторизован"
            )
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис недоступен"
        )

    user = User(**user_data)
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешён только администраторам"
        )
    return user


async def get_current_user(
    auth_client: AuthClient = Depends(get_auth_client)
) -> User:
    """
    Выполняет проверку авторизации текущего пользователя.

    :param auth_client: экземпляр AuthClient для выполнения запросов
    :return: объект User при успешной проверке
    :raises HTTPException: если пользователь не авторизован или сервис недоступен
    """
    try:
        user_data = await auth_client.get_user_profile()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещён: недостаточно прав"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не авторизован"
            )
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис недоступен"
        )

    return User(**user_data)
