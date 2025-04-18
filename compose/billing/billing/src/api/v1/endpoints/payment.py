from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends

from ..models.payment import (
    PaymentResponseDto,
    PaymentPayResponseDto,
    ProcessPaymentRequest, PaymentStatusRequest
)
from ....models.auth import User
from ....services.auth.client import get_current_user
from ....services.exceptions import CreatePaymentError, UpdatePaymentError
from ....services.integrations.exceptions import IntegrationCreatePaymentError
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
    status_code=HTTPStatus.CREATED,
    summary="Generate link to payment service",
    response_model=PaymentPayResponseDto
)
async def init_payment(
        payment_id: uuid.UUID,
        payment_method: PaymentIntegrations,
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

    integration = await integration_factory.get(payment_method)

    try:
        url = await integration.create(payment)
    except IntegrationCreatePaymentError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Creation is failed"
        )

    return PaymentPayResponseDto(url=url)


@router.post(
    path="/cancel/{payment_id}",
    status_code=HTTPStatus.CREATED,
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
        payment_service: PaymentServiceDep
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
    except UpdatePaymentError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Process is not updated"
        )

    return PaymentResponseDto(id=updated_payment.id)
