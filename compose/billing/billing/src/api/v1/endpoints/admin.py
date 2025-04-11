from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID

from src.schemas.admin_payments import PaymentSchema
from src.services.admin_payments import AdminPaymentService, get_admin_payment_service

router = APIRouter()


@router.get("/payments", response_model=List[PaymentSchema])
async def get_all_payments(service: AdminPaymentService = Depends(get_admin_payment_service)):
    """
    Получить все платежи всех пользователей.
    """
    payments = await service.get_all_payments()
    return payments


@router.get("/payments/user/{user_id}", response_model=List[PaymentSchema])
async def get_payments_by_user(user_id: UUID, service: AdminPaymentService = Depends(get_admin_payment_service)):
    """
    Получить все платежи пользователя с указанным user_id.
    """
    payments = await service.get_payments_by_user(user_id)
    return payments


@router.get("/payments/user/{user_id}/successful", response_model=List[PaymentSchema])
async def get_successful_payments(user_id: UUID, service: AdminPaymentService = Depends(get_admin_payment_service)):
    """
    Получить все успешные (завершённые) платежи пользователя.
    Предполагается, что успешный платеж имеет статус "successful".
    """
    payments = await service.get_successful_payments(user_id)
    return payments


@router.get("/payments/user/{user_id}/unsuccessful", response_model=List[PaymentSchema])
async def get_unsuccessful_payments(user_id: UUID, service: AdminPaymentService = Depends(get_admin_payment_service)):
    """
    Получить все неуспешные (отменённые) платежи пользователя.
    Предполагается, что неуспешный платеж имеет статус "cancelled".
    """
    payments = await service.get_unsuccessful_payments(user_id)
    return payments


@router.get("/payments/user/{user_id}/unprocessed", response_model=List[PaymentSchema])
async def get_unprocessed_payments(user_id: UUID, service: AdminPaymentService = Depends(get_admin_payment_service)):
    """
    Получить все необработанные (созданные) платежи пользователя.
    Предполагается, что необработанный платеж имеет статус "created".
    """
    payments = await service.get_unprocessed_payments(user_id)
    return payments
