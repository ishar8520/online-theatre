from fastapi import APIRouter, Depends
from uuid import UUID

from src.models.auth import User
from src.services.auth.client import get_current_admin_user
from src.schemas.admin_payments import PaymentSchema
from src.services.admin_payments import AdminPaymentService, get_admin_payment_service

router = APIRouter()


@router.get("/payments", response_model=list[PaymentSchema])
async def get_all_payments(
    service: AdminPaymentService = Depends(get_admin_payment_service),
    _is_admin: User = Depends(get_current_admin_user),
):
    payments = await service.get_all_payments()
    return payments


@router.get("/payments/user/{user_id}", response_model=list[PaymentSchema])
async def get_payments_by_user(
    user_id: UUID,
    service: AdminPaymentService = Depends(get_admin_payment_service),
    _is_admin: User = Depends(get_current_admin_user),
):
    """
    Получить все платежи пользователя с указанным user_id.
    """
    payments = await service.get_payments_by_user(user_id)
    return payments


@router.get("/payments/user/{user_id}/successful", response_model=list[PaymentSchema])
async def get_successful_payments(
    user_id: UUID,
    service: AdminPaymentService = Depends(get_admin_payment_service),
    _is_admin: User = Depends(get_current_admin_user),
):
    """
    Получить все успешные (завершённые) платежи пользователя.
    Предполагается, что успешный платеж имеет статус "successful".
    """
    payments = await service.get_successful_payments(user_id)
    return payments


@router.get("/payments/user/{user_id}/unsuccessful", response_model=list[PaymentSchema])
async def get_unsuccessful_payments(
    user_id: UUID,
    service: AdminPaymentService = Depends(get_admin_payment_service),
    _is_admin: User = Depends(get_current_admin_user),
):
    """
    Получить все неуспешные (отменённые) платежи пользователя.
    Предполагается, что неуспешный платеж имеет статус "cancelled".
    """
    payments = await service.get_unsuccessful_payments(user_id)
    return payments


@router.get("/payments/user/{user_id}/unprocessed", response_model=list[PaymentSchema])
async def get_unprocessed_payments(
    user_id: UUID,
    service: AdminPaymentService = Depends(get_admin_payment_service),
    _is_admin: User = Depends(get_current_admin_user),
):
    """
    Получить все необработанные (созданные) платежи пользователя.
    Предполагается, что необработанный платеж имеет статус "created".
    """
    payments = await service.get_unprocessed_payments(user_id)
    return payments
