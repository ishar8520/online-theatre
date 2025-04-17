from __future__ import annotations

import uuid

from pydantic import BaseModel

from ....service.models import PurchaseItemType


class PurchaseItemPropertyCreateResponseDto(BaseModel):
    name: str
    code: str
    value: str


class PurchaseItemResponseDto(BaseModel):
    id: uuid.UUID
    name: str
    quantity: int
    price: float
    type: PurchaseItemType
    props: list[PurchaseItemPropertyCreateResponseDto] | None


class PaymentResponseDto(BaseModel):
    id: uuid.UUID


class PaymentPayResponseDto(BaseModel):
    url: str
