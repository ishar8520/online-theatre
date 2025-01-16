from __future__ import annotations

import dataclasses

from fastapi import APIRouter

from .schemas import (
    UserRead,
    UserCreate,
    UserUpdate,
)
from .users import (
    fast_api_users,
    auth_backend,
)

auth_router = fast_api_users.get_auth_router(
    backend=auth_backend,
)
register_router = fast_api_users.get_register_router(
    user_schema=UserRead,
    user_create_schema=UserCreate,
)
reset_password_router = fast_api_users.get_reset_password_router()
users_router = fast_api_users.get_users_router(
    user_schema=UserRead,
    user_update_schema=UserUpdate,
)


@dataclasses.dataclass(kw_only=True)
class UsersRouters:
    auth: APIRouter
    register: APIRouter
    reset_password: APIRouter
    users: APIRouter


users_routers = UsersRouters(
    auth=auth_router,
    register=register_router,
    reset_password=reset_password_router,
    users=users_router,
)
