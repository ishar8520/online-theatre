from datetime import datetime

from pydantic import BaseModel


class YoomoneyUserModel(BaseModel):
    """
    Модель данных пользователя для YooMoney.

    :param user_id: уникальный идентификатор пользователя в системе
    """

    user_id: str


class YoomoneyPaymentModel(BaseModel):
    """
    Модель данных для инициализации платежа через YooMoney.

    :param amount: сумма платежа
    :param message: комментарий к платежу
    :param label: метка платежа для отслеживания
    """

    amount: float
    message: str
    label: str


class YoomoneyCallbackModel(BaseModel):
    """
    Модель данных для обработки callback уведомления от YooMoney.

    :param operation_id: уникальный идентификатор операции
    :param operation_label: метка операции, переданная при инициации платежа
    :param notification_type: тип уведомления (например, 'p2p-incoming')
    :param sender: идентификатор отправителя (номер кошелька), может быть пустым
    :param firstname: имя отправителя (опционально)
    :param lastname: фамилия отправителя (опционально)
    :param fathername: отчество отправителя (опционально)
    :param zip: почтовый индекс отправителя (опционально)
    :param city: город отправителя (опционально)
    :param street: улица отправителя (опционально)
    :param building: номер дома отправителя (опционально)
    :param flat: номер квартиры отправителя (опционально)
    :param suite: корпус/строение отправителя (опционально)
    :param phone: телефон отправителя (опционально)
    :param email: email отправителя (опционально)
    :param label: метка платежа для сопоставления с вашим приложением
    :param codepro: флаг защиты платежа кодом ('true' или 'false')
    :param bill_id: внутренний идентификатор счёта в YooMoney (опционально)
    :param withdraw_amount: сумма списания с отправителя
    :param currency: валюта платежа (ISO-код)
    :param datetime: дата и время проведения операции
    :param sha1_hash: SHA-1 хэш данных для проверки подлинности уведомления
    """

    operation_id: str
    operation_label: str
    notification_type: str
    sender: str = ''
    firstname: str = ''
    lastname: str = ''
    fathername: str = ''
    zip: str = ''
    city: str = ''
    street: str = ''
    building: str = ''
    flat: str = ''
    suite: str = ''
    phone: str = ''
    email: str = ''
    label: str
    codepro: str = 'false'
    bill_id: str = ''
    withdraw_amount: str
    currency: str
    datetime: datetime
    sha1_hash: str
