from __future__ import annotations

import enum
import uuid
from typing import Optional

from pydantic import BaseModel


class PaymentStatus(enum.StrEnum):
    """
    Перечисление возможных статусов платежа.

    :param PAID: оплачено
    :param UNPAID: не оплачено
    :param FAILED: неуспешно
    :param CANCELED: отменено
    :param REFUNDED: возвращено
    """

    PAID = 'paid'
    UNPAID = 'unpaid'
    FAILED = 'failed'
    CANCELED = 'canceled'
    REFUNDED = 'refunded'


class PurchaseItemType(enum.StrEnum):
    """
    Перечисление типов позиций покупки.

    :param SUBSCRIBE: подписка
    :param MOVIE: кино
    """

    SUBSCRIBE = 'subscribe'
    MOVIE = 'movie'


class PurchaseItemPropertyCreateDto(BaseModel):
    """
    DTO для создания свойства позиции покупки.

    :param name: наименование свойства
    :param code: код свойства (для уникальной идентификации)
    :param value: значение свойства
    """

    name: str
    code: str
    value: str


class PurchaseItemCreateDto(BaseModel):
    """
    DTO для создания позиции покупки.

    :param name: наименование товара или услуги
    :param quantity: количество единиц
    :param price: цена за единицу
    :param type: тип позиции (из PurchaseItemType)
    :param props: список свойств позиции (PurchaseItemPropertyCreateDto)
    """

    name: str
    quantity: int
    price: float
    type: PurchaseItemType
    props: list[PurchaseItemPropertyCreateDto]


class PaymentCreateDto(BaseModel):
    """
    DTO для создания нового платежа.

    :param user_id: UUID пользователя, совершающего платёж
    :param status: начальный статус платежа (по умолчанию UNPAID)
    :param items: список позиций покупки (PurchaseItemCreateDto)
    """

    user_id: uuid.UUID
    status: PaymentStatus = PaymentStatus.UNPAID
    items: list[PurchaseItemCreateDto]


class PaymentUpdateDto(BaseModel):
    """
    DTO для обновления параметров платежа.

    :param status: новый статус платежа (опционально)
    :param ps_name: название платёжной системы (опционально)
    :param ps_invoice_id: UUID счёта в платёжной системе (опционально)
    """

    status: Optional[PaymentStatus] = None
    ps_name: Optional[str] = None
    ps_invoice_id: Optional[uuid.UUID] = None
