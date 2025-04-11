from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.sqlalchemy import get_async_session
from src.models.sqlalchemy import Payment


class AdminPaymentService:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def get_all_payments(self) -> list[Payment]:
        """
        Получает все платежи всех пользователей.
        """
        async with self.postgres_session as session:
            result = await session.scalars(select(Payment))
            return list(result.all())

    async def get_payments_by_user(self, user_id: UUID) -> list[Payment]:
        """
        Получает все платежи пользователя с указанным user_id.
        """
        async with self.postgres_session as session:
            result = await session.scalars(
                select(Payment).where(Payment.user_id == user_id)
            )
            return list(result.all())

    async def get_successful_payments(self, user_id: UUID) -> list[Payment]:
        """
        Получает все успешные (завершённые) платежи пользователя.
        Предполагается, что успешный платеж имеет статус "successful".
        """
        async with self.postgres_session as session:
            result = await session.scalars(
                select(Payment).where(
                    Payment.user_id == user_id,
                    Payment.status == "successful"
                )
            )
            return list(result.all())

    async def get_unsuccessful_payments(self, user_id: UUID) -> list[Payment]:
        """
        Получает все неуспешные (отменённые) платежи пользователя.
        Предполагается, что неуспешный платеж имеет статус "cancelled".
        """
        async with self.postgres_session as session:
            result = await session.scalars(
                select(Payment).where(
                    Payment.user_id == user_id,
                    Payment.status == "cancelled"
                )
            )
            return list(result.all())

    async def get_unprocessed_payments(self, user_id: UUID) -> list[Payment]:
        """
        Получает все необработанные (созданные) платежи пользователя.
        Предполагается, что необработанный платеж имеет статус "created".
        """
        async with self.postgres_session as session:
            result = await session.scalars(
                select(Payment).where(
                    Payment.user_id == user_id,
                    Payment.status == "created"
                )
            )
            return list(result.all())


@lru_cache()
def get_admin_payment_service(
    postgres_session: AsyncSession = Depends(get_async_session),
) -> AdminPaymentService:
    """
    Фабрика сервиса для работы с платежами с использованием кеширования.
    """
    return AdminPaymentService(postgres_session)
