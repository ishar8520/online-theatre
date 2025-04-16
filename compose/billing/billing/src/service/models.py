from __future__ import annotations

import enum
import uuid

from pydantic import BaseModel


class PaymentStatus(enum.StrEnum):
    CREATED = 'created'
    PAID = 'paid'
    UNPAID = 'unpaid'


class PurchaseItemType(enum.StrEnum):
    SUBSCRIBE = 'subscribe'
    MOVIE = 'movie'


class PurchaseItemPropertyCreateDto(BaseModel):
    name: str
    code: str
    value: str


class PurchaseItemCreateDto(BaseModel):
    name: str
    quantity: int
    price: float
    type: PurchaseItemType
    props: list[PurchaseItemPropertyCreateDto]


class PaymentCreateDto(BaseModel):
    user_id: uuid.UUID
    status: PaymentStatus = PaymentStatus.CREATED
    items: list[PurchaseItemCreateDto]

