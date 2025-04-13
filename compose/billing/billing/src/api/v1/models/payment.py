from __future__ import annotations

import enum
import uuid

from pydantic import BaseModel


class PaymentStatus(enum.StrEnum):
    CREATED = 'created'
    PAID = 'paid'
    UNPAID = 'unpaid'


class PurchaseItemCreateDto(BaseModel):
    name: str
    quantity: int
    price: float


class PurchaseItemResponseDto(PurchaseItemCreateDto):
    id: uuid.UUID


class PaymentResponseDto(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: PaymentStatus
    items: list[PurchaseItemCreateDto]


class PaymentUpdateDto(BaseModel):
    status: PaymentStatus


class PaymentPayResponseDto(BaseModel):
    url: str
