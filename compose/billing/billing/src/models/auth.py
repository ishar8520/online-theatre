from __future__ import annotations

import uuid

from pydantic import BaseModel


class User(BaseModel):
    """
    Модель данных пользователя.

    :param id: UUID пользователя
    :param login: логин пользователя (опционально)
    :param email: электронная почта пользователя (опционально)
    :param is_superuser: флаг суперпользователя (по умолчанию False)
    """

    id: uuid.UUID
    login: str | None = None
    email: str | None = None
    is_superuser: bool = False
