from __future__ import annotations

import enum
import uuid
from typing import Optional

from pydantic import BaseModel


class PaymentStatus(enum.StrEnum):
    CREATED = 'created'
    PAID = 'paid'
    UNPAID = 'unpaid'
    CANCELED = 'canceled'


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


class PaymentUpdateDto(BaseModel):
    status: Optional[PaymentStatus] = None
    ps_name: Optional[str] = None
    ps_invoice_id: Optional[uuid.UUID] = None
