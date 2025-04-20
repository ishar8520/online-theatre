from __future__ import annotations


class CreatePaymentError(Exception):
    """
    Исключение, возникающее при ошибке создания платежа.

    Используется в сервисе PaymentService при неудачной попытке добавить новый платёж.
    """

    pass


class UpdatePaymentError(Exception):
    """
    Исключение, возникающее при ошибке обновления платежа.

    Используется в сервисе PaymentService при неудачной попытке изменить статус или данные существующего платежа.
    """

    pass
