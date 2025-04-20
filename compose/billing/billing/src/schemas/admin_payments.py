from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PaymentSchema(BaseModel):
    """
    Схема данных платежа для административных операций.

    :param id: UUID платежа
    :param user_id: UUID пользователя, создавшего платёж
    :param ps_name: название платёжной системы (опционально)
    :param ps_invoice_id: UUID счёта в платёжной системе (опционально)
    :param status: статус платежа
    :param created_at: время создания платежа
    :param modified_at: время последнего обновления платежа
    """

    id: UUID
    user_id: UUID
    ps_name: str | None = None
    ps_invoice_id: UUID | None = None
    status: str
    created_at: datetime
    modified_at: datetime

    class Config:
        """
        Настройки Pydantic для этой схемы.

        from_attributes = True позволяет заполнять поля модели
        из атрибутов ORM-объекта при использовании .from_orm().
        """

        from_attributes = True
