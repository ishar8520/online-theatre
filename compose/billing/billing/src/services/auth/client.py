from __future__ import annotations

from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, status

from src.models.auth import User
from src.core.config import settings
from src.services.auth.token import TokenDep

from src.dependencies import HTTPXClientDep


class AuthClient:
    httpx_client: httpx.AsyncClient
    token: str

    def __init__(self, *, httpx_client: httpx.AsyncClient, token: str) -> None:
        self.httpx_client = httpx_client
        self.token = token

    async def get_user_profile(self) -> dict:
        response = await self.httpx_client.get(
            url=settings.auth.user_profile_url,
            headers=self.get_headers(),
        )
        response.raise_for_status()
        return response.json()

    def get_headers(self) -> dict:
        return {
            'X-Request-Id': 'billing',
            'Authorization': f'Bearer {self.token}',
        }


def get_auth_client(httpx_client: HTTPXClientDep, token: TokenDep) -> AuthClient:
    return AuthClient(httpx_client=httpx_client, token=token)


AuthClientDep = Annotated[AuthClient, Depends(get_auth_client)]


async def get_current_admin_user(
    auth_client: AuthClient = Depends(get_auth_client)
) -> User:
    """Метод для проверки авторизации и прав администратора."""
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
