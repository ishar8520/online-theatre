from __future__ import annotations


class FastAPIUsersException(Exception):
    pass


class InvalidID(FastAPIUsersException):
    pass


class UserAlreadyExists(FastAPIUsersException):
    pass


class UserNotExists(FastAPIUsersException):
    pass
