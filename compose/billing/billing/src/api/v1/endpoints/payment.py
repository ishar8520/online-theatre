from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter

from ..models.payment import (
    PurchaseItemCreateDto,
    PaymentResponseDto,
    PaymentPayResponseDto
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

    return PaymentResponseDto()


@router.post(
    path='/pay/{payment_id}',
    status_code=HTTPStatus.CREATED,
    summary='Generate link to payment service',
    response_model=PaymentPayResponseDto
)
async def create(
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
async def create(
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
async def create(
        payment_id: uuid.UUID,
        payment_service: PaymentServiceDep
) -> PaymentResponseDto:

    return PaymentResponseDto()
