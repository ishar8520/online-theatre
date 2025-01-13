from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi_users.db import (
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyUserDatabase,
)

from ...db.sqlalchemy import (
    AuthBase,
    AsyncSessionDep,
)


class User(SQLAlchemyBaseUserTableUUID, AuthBase):
    pass


async def get_user_database(session: AsyncSessionDep) -> SQLAlchemyUserDatabase:
    return SQLAlchemyUserDatabase(session=session, user_table=User)


UserDatabaseDep = Annotated[SQLAlchemyUserDatabase, Depends(get_user_database)]
