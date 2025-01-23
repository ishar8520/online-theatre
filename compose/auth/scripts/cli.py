from __future__ import annotations

import asyncio
from sqlalchemy.exc import SQLAlchemyError
from typer import Typer
import sys

sys.path.append('..')

from auth.models.sqlalchemy import User
from auth.services.users.password import PasswordHelper
from auth.db.sqlalchemy import engine
from sqlalchemy import insert

app = Typer()


@app.command()
def create_superuser(login: str, password: str):
    asyncio.run(create_superuser_async(login=login, password=password))


async def create_superuser_async(login: str, password: str):
    async with engine.begin() as connection:

        superuser = {
            "login": login,
            "password": PasswordHelper().hash(password),
            "is_superuser": True
        }

        statement = insert(User).values(superuser)

        try:
            await connection.execute(statement=statement)
            await connection.commit()
            print(f"Superuser with login={login} is created")
        except SQLAlchemyError:
            print("Creation of superuser is failed")
            await connection.rollback()
        finally:
            await connection.close()


if __name__ == '__main__':
    app()
