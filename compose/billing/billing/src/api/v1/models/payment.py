from __future__ import annotations

import datetime
import enum
import uuid

from pydantic import BaseModel

from src.services.integrations.models import PaymentIntegrations


class PaymentResponseDto(BaseModel):
    """
    DTO ответа при создании или отмене платежа.

    :param id: UUID созданного или обновлённого платежа
    """

    id: uuid.UUID


class PaymentPayResponseDto(BaseModel):
    """
    DTO ответа при генерации ссылки на платёж.

    :param url: URL для перехода на страницу оплаты
    """

    url: str


class PaymentRefundResponseDto(BaseModel):
    """
    DTO ответа при генерации ссылки на возврат платежа.

    :param url: URL для перехода на страницу возврата
    """

    url: str


class PaymentStatusRequest(enum.StrEnum):
    """
    Тип запроса статуса платежа.

    :param SUCCESS: успешный платёж
    :param FAILED: неуспешный платёж
    """

    SUCCESS = 'success'
    FAILED = 'failed'


class ProcessPaymentRequest(BaseModel):
    """
    DTO запроса для обработки результата платежа.

    :param service: интеграция, через которую пришло уведомление
    :param status: новый статус платежа ('success' или 'failed')
    :param label: UUID метки платежа
    :param amount: сумма платежа
    :param withdraw_amount: сумма фактического списания
    :param datetime: дата и время проведения операции
    """

    service: PaymentIntegrations
    status: PaymentStatusRequest
    label: uuid.UUID
    amount: float
    withdraw_amount: float
    datetime: datetime.datetime


class InitPaymentRequest(BaseModel):
    """
    DTO запроса для инициализации платежа.

    :param payment_method: способ оплаты из списка интеграций
    """

    payment_method: PaymentIntegrations


class RefundPaymentRequest(BaseModel):
    """
    DTO запроса для инициации возврата платежа.

    :param payment_method: способ возврата из списка интеграций
    """

    payment_method: PaymentIntegrations
