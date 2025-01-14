from __future__ import annotations

from typing import cast, Type, Annotated

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.models import UserProtocol

from ...db.sqlalchemy import AsyncSessionDep
from ...models.sqlalchemy import User


async def get_user_database(session: AsyncSessionDep) -> SQLAlchemyUserDatabase:
    return SQLAlchemyUserDatabase(session=session, user_table=cast(Type[UserProtocol], User))


UserDatabaseDep = Annotated[SQLAlchemyUserDatabase, Depends(get_user_database)]
