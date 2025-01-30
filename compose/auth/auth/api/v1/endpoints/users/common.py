from __future__ import annotations

from enum import Enum
from typing import Union

from pydantic import BaseModel


class ErrorModel(BaseModel):
    detail: Union[str, dict[str, str]]


class ErrorCode(str, Enum):
    REGISTER_USER_ALREADY_EXISTS = 'REGISTER_USER_ALREADY_EXISTS'
    LOGIN_BAD_CREDENTIALS = 'LOGIN_BAD_CREDENTIALS'
    REFRESH_INVALID_TOKEN = 'REFRESH_INVALID_TOKEN'
    UPDATE_USER_LOGIN_ALREADY_EXISTS = 'UPDATE_USER_LOGIN_ALREADY_EXISTS'
    OAUTH_INVALID_STATE_TOKEN = 'OAUTH_INVALID_STATE_TOKEN'
    OAUTH_EMAIL_NOT_AVAILABLE = 'OAUTH_EMAIL_NOT_AVAILABLE'
