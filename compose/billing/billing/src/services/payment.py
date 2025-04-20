from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy import (
    select,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.sqlalchemy import AsyncSessionDep
from src.models.sqlalchemy import Payment, PurchaseItem, PurchaseItemProperty
from src.services.exceptions import CreatePaymentError, UpdatePaymentError
from src.services.models import PaymentStatus, PaymentUpdateDto, PurchaseItemCreateDto


class PaymentService:
    """Сервис для работы с платежами."""

    _session: AsyncSession

    def __init__(self, session: AsyncSession):
        """Инициализирует сервис сессией AsyncSession."""
        self._session = session

    async def get_by_id(self, id: uuid.UUID) -> Payment | None:
        """Возвращает объект Payment по его UUID или None."""
        statement = select(Payment).where(Payment.id == id)
        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def add(
        self,
        user_id: uuid.UUID,
        purchase_items: list[PurchaseItemCreateDto]
    ) -> Payment:
        """
        Создает новый платеж с позициями и сохраняет его в БД.

        :param user_id: UUID пользователя, совершающего платёж
        :param purchase_items: список DTO позиций для создания платежа
        :return: Сохранённый объект Payment
        :raise CreatePaymentError: при ошибке сохранения в БД
        """
        total_price: float = 0.0
        payment_items = []
        for item in purchase_items:
            total_price += item.quantity * item.price

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
        """
        Обновляет поля платежа согласно DTO и сохраняет изменения.

        :param payment: объект Payment для обновления
        :param payment_update: DTO с новыми значениями полей
        :return: Обновлённый объект Payment
        :raise UpdatePaymentError: при ошибке сохранения в БД
        """
        fields = payment_update.model_dump(exclude_unset=True)
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


def get_payment_service(session: AsyncSessionDep) -> PaymentService:
    """Фабрика для создания экземпляра PaymentService из зависимости AsyncSession."""
    return PaymentService(session)


PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
