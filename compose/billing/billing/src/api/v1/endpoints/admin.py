from uuid import UUID

from fastapi import APIRouter, Depends

from src.models.auth import User
from src.models.sqlalchemy import Payment
from src.schemas.admin_payments import PaymentSchema
from src.services.admin_payments import AdminPaymentService, get_admin_payment_service
from src.services.auth.client import get_current_admin_user

router = APIRouter()


@router.get("/payments", response_model=list[PaymentSchema])
async def get_all_payments(
    service: AdminPaymentService = Depends(get_admin_payment_service),
    _is_admin: User = Depends(get_current_admin_user),
) -> list[Payment]:
    """Получить все платежи."""
    payments = await service.get_all_payments()
    return payments


@router.get("/payments/user/{user_id}", response_model=list[PaymentSchema])
async def get_payments_by_user(
    user_id: UUID,
    service: AdminPaymentService = Depends(get_admin_payment_service),
    _is_admin: User = Depends(get_current_admin_user),
) -> list[Payment]:
    """Получить все платежи пользователя с указанным user_id."""
    payments = await service.get_payments_by_user(user_id)
    return payments


@router.get("/payments/user/{user_id}/successful", response_model=list[PaymentSchema])
async def get_successful_payments(
    user_id: UUID,
    service: AdminPaymentService = Depends(get_admin_payment_service),
    _is_admin: User = Depends(get_current_admin_user),
) -> list[Payment]:
    """
    Получить все успешные (завершённые) платежи пользователя.

    Успешный платеж имеет статус "successful".
    """
    payments = await service.get_successful_payments(user_id)
    return payments


@router.get("/payments/user/{user_id}/unsuccessful", response_model=list[PaymentSchema])
async def get_unsuccessful_payments(
    user_id: UUID,
    service: AdminPaymentService = Depends(get_admin_payment_service),
    _is_admin: User = Depends(get_current_admin_user),
) -> list[Payment]:
    """
    Получить все неуспешные (отменённые) платежи пользователя.

    Неуспешный платеж имеет статус "cancelled".
    """
    payments = await service.get_unsuccessful_payments(user_id)
    return payments


@router.get("/payments/user/{user_id}/unprocessed", response_model=list[PaymentSchema])
async def get_unprocessed_payments(
    user_id: UUID,
    service: AdminPaymentService = Depends(get_admin_payment_service),
    _is_admin: User = Depends(get_current_admin_user),
) -> list[Payment]:
    """
    Получить все необработанные (созданные) платежи пользователя.

    Необработанный платеж имеет статус "created".
    """
    payments = await service.get_unprocessed_payments(user_id)
    return payments
