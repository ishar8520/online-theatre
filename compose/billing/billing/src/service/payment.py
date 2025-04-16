from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    select,
)

from .exceptions import CreatePaymentError
from .models import PurchaseItemCreateDto, PaymentStatus
from ..db.sqlalchemy import AsyncSessionDep
from ..models.sqlalchemy import (
    Payment,
    PurchaseItem,
    PurchaseItemProperty
)


class PaymentService:
    _session: AsyncSession

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: uuid.UUID) -> Payment | None:
        statement = select(Payment).where(Payment.id == id)
        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def create(
            self,
            user_id: uuid.UUID,
            purchase_items: list[PurchaseItemCreateDto]
    ) -> Payment:

        payment_items = []
        for item in purchase_items:
            payment_items.append(
                PurchaseItem(
                    name=item.name,
                    quantity=item.quantity,
                    price=item.price,
                    type=item.type,
                    properties=[PurchaseItemProperty(**v.model_dump()) for v in item.props]
                )
            )

        payment = Payment(
            user_id=user_id,
            status=PaymentStatus.CREATED,
            items=payment_items
        )

        self._session.add(payment)

        try:
            await self._session.commit()
            await self._session.refresh(payment)
        except SQLAlchemyError:
            await self._session.rollback()
            raise CreatePaymentError

        return payment


def get_payment_service(session: AsyncSessionDep):
    return PaymentService(session)


PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
