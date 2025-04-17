from __future__ import annotations

import enum
import uuid
from datetime import datetime

from pydantic import BaseModel

from ....service.integrations.models import PaymentIntegrations
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


class PaymentStatusRequest(enum.StrEnum):
    SUCCESS = 'success'
    FAILED = 'failed'


class ProcessPaymentRequest(BaseModel):
    service: PaymentIntegrations
    status: PaymentStatusRequest
    label: uuid.UUID
    amount: float
    withdraw_amount: float
    datetime: datetime
