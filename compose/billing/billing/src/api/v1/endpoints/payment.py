from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from ..models.payment import (
    PaymentResponseDto,
    PaymentPayResponseDto
)
from ....service.exceptions import CreatePaymentError
from ....service.models import (
    PurchaseItemCreateDto
)
from ....service.payment import PaymentServiceDep

router = APIRouter()


@router.put(
    path='/create',
    status_code=HTTPStatus.CREATED,
    summary='New purchase',
    response_model=PaymentResponseDto
)
async def create(
        purchase_items: list[PurchaseItemCreateDto],
        payment_service: PaymentServiceDep
) -> PaymentResponseDto:
    user_id = "550e8400-e29b-41d4-a716-446655440000"

    try:
        created_payment = await payment_service.create_payment(
            user_id=user_id,
            purchase_items=purchase_items
        )
    except CreatePaymentError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Payment is failed'
        )

    return PaymentResponseDto(
        id=created_payment.id
    )


@router.post(
    path='/pay/{payment_id}',
    status_code=HTTPStatus.CREATED,
    summary='Generate link to payment service',
    response_model=PaymentPayResponseDto
)
async def pay(
        payment_id: uuid.UUID,
        payment_service: PaymentServiceDep
) -> PaymentPayResponseDto:

    return PaymentPayResponseDto()


@router.post(
    path='/cancel/{payment_id}',
    status_code=HTTPStatus.CREATED,
    summary='Cancel payment',
    response_model=bool
)
async def cancel(
        payment_id: uuid.UUID,
        payment_service: PaymentServiceDep
) -> bool:

    return True


@router.post(
    path='/update/{payment_id}',
    status_code=HTTPStatus.CREATED,
    summary='Update information of payment',
    response_model=PaymentResponseDto
)
async def update(
        payment_id: uuid.UUID,
        payment_service: PaymentServiceDep
) -> PaymentResponseDto:

    return PaymentResponseDto()
