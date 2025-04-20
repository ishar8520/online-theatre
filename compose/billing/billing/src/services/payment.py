from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    select,
)

from .exceptions import (
    CreatePaymentError,
    UpdatePaymentError
)
from .models import (
    PurchaseItemCreateDto,
    PaymentStatus,
    PaymentUpdateDto
)
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

    async def add(
            self,
            user_id: uuid.UUID,
            purchase_items: list[PurchaseItemCreateDto]
    ) -> Payment:

        total_price = 0
        payment_items = []
        for item in purchase_items:
            total_price += item.quantity*item.price

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
            status=PaymentStatus.UNPAID,
            price=total_price,
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

    async def update(
            self,
            payment: Payment,
            payment_update: PaymentUpdateDto
    ) -> Payment:
        fields = payment_update.model_dump(exclude_unset=True)
        print(fields)
        for key, value in fields.items():
            setattr(payment, key, value)

        self._session.add(payment)

        try:
            await self._session.commit()
            await self._session.refresh(payment)
        except SQLAlchemyError:
            await self._session.rollback()
            raise UpdatePaymentError

        return payment


def get_payment_service(session: AsyncSessionDep):
    return PaymentService(session)


PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
