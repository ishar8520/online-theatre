from __future__ import annotations

import uuid
from http import HTTPStatus

import httpx
from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.models.payment import (
    InitPaymentRequest,
    PaymentPayResponseDto,
    PaymentRefundResponseDto,
    PaymentResponseDto,
    PaymentStatusRequest,
    ProcessPaymentRequest,
    RefundPaymentRequest,
)
from src.dependencies.httpx import get_httpx_client
from src.models.auth import User
from src.services.auth.client import get_current_admin_user, get_current_user
from src.services.exceptions import CreatePaymentError, UpdatePaymentError
from src.services.integrations.exceptions import IntegrationCreatePaymentError, IntegrationRefundPaymentError
from src.services.integrations.factory import IntegrationFactoryDep
from src.services.models import PaymentStatus, PaymentUpdateDto, PurchaseItemCreateDto
from src.services.payment import PaymentServiceDep
from src.core.config import settings


router = APIRouter()


@router.put(
    path="/create",
    status_code=HTTPStatus.CREATED,
    summary="New purchase",
    response_model=PaymentResponseDto
)
async def create(
    purchase_items: list[PurchaseItemCreateDto],
    payment_service: PaymentServiceDep,
    user: User = Depends(get_current_user),
) -> PaymentResponseDto:
    """
    Создаёт новую покупку (платёж).

    :return: Результат создания новой покупки
    """
    try:
        created_payment = await payment_service.add(
            user_id=user.id,
            purchase_items=purchase_items
        )
    except CreatePaymentError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Payment is failed"
        )

    return PaymentResponseDto(
        id=created_payment.id
    )


@router.post(
    path="/init_payment/{payment_id}",
    status_code=HTTPStatus.OK,
    summary="Generate link to payment service",
    response_model=PaymentPayResponseDto
)
async def init_payment(
    payment_id: uuid.UUID,
    payment_request: InitPaymentRequest,
    payment_service: PaymentServiceDep,
    integration_factory: IntegrationFactoryDep,
    user: User = Depends(get_current_user),
) -> PaymentPayResponseDto:
    """
    Генерирует ссылку на платёжный сервис для инициации платежа.

    :param payment_id: UUID платежа
    :param payment_request: данные для инициализации платежа
    :param payment_service: сервис обработки платежей
    :param integration_factory: фабрика интеграций для методов оплаты
    :param user: текущий пользователь
    :return: DTO с URL для оплаты
    """
    payment = await payment_service.get_by_id(id=payment_id)

    if payment is None or payment.user_id != user.id:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            "Payment is not found"
        )

    if payment.status == PaymentStatus.CANCELED:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            "Payment is canceled"
        )

    integration = await integration_factory.get(payment_request.payment_method)

    try:
        url = await integration.create(payment)
    except IntegrationCreatePaymentError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Creation is failed"
        )

    return PaymentPayResponseDto(url=url)


@router.post(
    path="/refund/{payment_id}",
    status_code=HTTPStatus.OK,
    summary="Return refund link to payment service",
    response_model=PaymentRefundResponseDto
)
async def refund(
    payment_id: uuid.UUID,
    payment_request: RefundPaymentRequest,
    payment_service: PaymentServiceDep,
    integration_factory: IntegrationFactoryDep,
    user: User = Depends(get_current_user),
) -> PaymentRefundResponseDto:
    """
    Формирует ссылку для возврата платежа через платёжный сервис.

    :param payment_id: UUID платежа
    :param payment_request: данные для возврата платежа
    :param payment_service: сервис обработки платежей
    :param integration_factory: фабрика интеграций для методов оплаты
    :param user: текущий пользователь
    :return: DTO с URL для возврата платежа
    """
    payment = await payment_service.get_by_id(id=payment_id)

    if payment is None or payment.user_id != user.id:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            "Payment is not found"
        )

    if payment.status != PaymentStatus.PAID:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            "Payment is not paid"
        )

    integration = await integration_factory.get(payment_request.payment_method)

    try:
        url = await integration.refund(payment)
    except IntegrationRefundPaymentError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Refund is failed"
        )

    return PaymentRefundResponseDto(url=url)


@router.post(
    path="/cancel/{payment_id}",
    status_code=HTTPStatus.OK,
    summary="Cancel payment",
    response_model=PaymentResponseDto
)
async def cancel(
    payment_id: uuid.UUID,
    payment_service: PaymentServiceDep,
    user: User = Depends(get_current_user),
) -> PaymentResponseDto:
    """
    Отменяет указанный платёж.

    :param payment_id: UUID платежа
    :param payment_service: сервис обработки платежей
    :param user: текущий пользователь
    :return: DTO с ID отменённого платежа
    """
    payment = await payment_service.get_by_id(id=payment_id)

    if payment is None or payment.user_id != user.id:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            "Payment is not found"
        )

    if payment.status == PaymentStatus.PAID:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            "Payment is paid"
        )

    update_data = PaymentUpdateDto(status=PaymentStatus.CANCELED)
    try:
        await payment_service.update(payment, update_data)
    except UpdatePaymentError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Update is failed"
        )

    return PaymentResponseDto(id=payment.id)


@router.post(
    path="/process/{payment_id}",
    status_code=HTTPStatus.OK,
    summary="Process result of payment",
    response_model=PaymentResponseDto
)
async def process(
    payment_id: uuid.UUID,
    payment_info: ProcessPaymentRequest,
    payment_service: PaymentServiceDep,
    user: User = Depends(get_current_admin_user),
    httpx_client: httpx.AsyncClient = Depends(get_httpx_client)
) -> PaymentResponseDto:
    """
    Обрабатывает результат платежа и отправляет уведомление.

    :param payment_id: UUID платежа
    :param payment_info: данные с результатом платежа
    :param payment_service: сервис обработки платежей
    :param user: текущий администратор
    :param httpx_client: HTTP-клиент для отправки уведомления
    :return: DTO с ID обновлённого платежа
    """
    payment = await payment_service.get_by_id(id=payment_id)

    if payment is None:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            "Payment is not found"
        )

    if payment.status != PaymentStatus.UNPAID:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            "Payment is already processed"
        )

    try:
        status = PaymentStatus.FAILED
        if payment_info.status == PaymentStatusRequest.SUCCESS:
            status = PaymentStatus.PAID
        update_data = PaymentUpdateDto(
            status=status,
            ps_name=payment_info.service
        )
        updated_payment = await payment_service.update(payment, update_data)
        data = {
            'user_id': str(payment.user_id),
            'payment_status': payment_info.status,
            'notification_type': 'email'
        }
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        await httpx_client.post(
            f'{settings.notification.schema}://{settings.notification.host}:{settings.notification.port}/notification/api/v1/events/payment_status',
            headers=headers,
            json=data,
        )
    except UpdatePaymentError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Process is not updated"
        )

    return PaymentResponseDto(id=updated_payment.id)
