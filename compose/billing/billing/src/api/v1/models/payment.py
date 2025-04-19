from __future__ import annotations

import enum
import uuid
import datetime

from pydantic import BaseModel

from ....services.integrations.models import PaymentIntegrations
from ....services.models import PurchaseItemType


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


class PaymentRefundResponseDto(BaseModel):
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
    datetime: datetime.datetime
