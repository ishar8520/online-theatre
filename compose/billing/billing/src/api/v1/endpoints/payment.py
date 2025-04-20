from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends

from ..models.payment import (
    PaymentResponseDto,
    PaymentPayResponseDto,
    ProcessPaymentRequest,
    PaymentStatusRequest,
    PaymentRefundResponseDto, InitPaymentRequest, RefundPaymentRequest
)
from ....models.auth import User
from ....dependencies.httpx import httpx, get_httpx_client
from ....services.auth.client import get_current_user, get_current_admin_user
from ....services.exceptions import CreatePaymentError, UpdatePaymentError
from ....services.integrations.exceptions import (
    IntegrationCreatePaymentError,
    IntegrationRefundPaymentError
)
from ....services.integrations.factory import IntegrationFactoryDep
from ....services.integrations.models import PaymentIntegrations
from ....services.models import (
    PurchaseItemCreateDto,
    PaymentUpdateDto,
    PaymentStatus
)
from ....services.payment import PaymentServiceDep

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
            f'http://notification-service:8000/notification/api/v1/events/payment_status',
            headers=headers,
            json=data 
        )
    except UpdatePaymentError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Process is not updated"
        )

    return PaymentResponseDto(id=updated_payment.id)
