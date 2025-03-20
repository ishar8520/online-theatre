from __future__ import annotations

import uuid

from pydantic import BaseModel


class AuthTokens(BaseModel):
    token_type: str
    access_token: str
    refresh_token: str


class User(BaseModel):
    id: uuid.UUID
    login: str | None
    email: str | None
    is_superuser: bool
