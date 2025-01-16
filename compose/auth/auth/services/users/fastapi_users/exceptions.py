from __future__ import annotations

from typing import Any


class FastAPIUsersException(Exception):
    pass


class InvalidID(FastAPIUsersException):
    pass


class UserAlreadyExists(FastAPIUsersException):
    pass


class UserNotExists(FastAPIUsersException):
    pass


class InvalidResetPasswordToken(FastAPIUsersException):
    pass


class InvalidPasswordException(FastAPIUsersException):
    def __init__(self, reason: Any) -> None:
        self.reason = reason
