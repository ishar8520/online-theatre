from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.sqlalchemy import AsyncSessionDep


class PaymentService:
    _session: AsyncSession

    def __init__(self, session: AsyncSession):
        self._session = session

    pass


def get_payment_service(session: AsyncSessionDep):
    return PaymentService(session)


PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
