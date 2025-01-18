from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from ..utils.auth.sqlalchemy import Role
import pytest_asyncio


@pytest_asyncio.fixture(scope='function')
async def create_role(async_session: AsyncSession):
    new_role = Role(name="subscribers", code="subscribers")
    async_session.add(new_role)
    await async_session.commit()
    await async_session.refresh(new_role)

    yield new_role

    await async_session.delete(new_role)
    await async_session.commit()
