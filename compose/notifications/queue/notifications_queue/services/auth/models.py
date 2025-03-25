from __future__ import annotations

import datetime
import uuid

from pydantic import (
    BaseModel,
    EmailStr,
)


class AuthTokens(BaseModel):
    token_type: str
    access_token: str
    refresh_token: str


class User(BaseModel):
    id: uuid.UUID
    login: str | None
    email: EmailStr | None
    is_superuser: bool
    created: datetime.datetime
    modified: datetime.datetime


class UsersListParams(BaseModel):
    user_id: uuid.UUID | None = None
    user_created: datetime.datetime | None = None
    page_size: int | None = None
