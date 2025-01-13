from __future__ import annotations

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
verify_router = fast_api_users.get_verify_router(
    user_schema=UserRead,
)
users_router = fast_api_users.get_users_router(
    user_schema=UserRead,
    user_update_schema=UserUpdate,
)
