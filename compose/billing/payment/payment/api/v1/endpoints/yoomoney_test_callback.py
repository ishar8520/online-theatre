from typing import Any
from urllib.parse import urlencode

import aiohttp
from fastapi import APIRouter

from payment.api.v1.models.yoomoney import YoomoneyCallbackModel

router = APIRouter()


@router.post('/_test_callback')
async def test_callback_success(
    callback: YoomoneyCallbackModel,
    amount: float,
    payment_status: bool
) -> Any:
    """
    Тестовый эндпоинт для проверки обработки callback от YooMoney.

    :param callback: модель данных callback от YooMoney
    :param amount: ожидаемая сумма платежа
    :param payment_status: ожидаемый статус платежа (True — оплачен, False — отклонён)
    :return: результат выполнения внутренней проверки (_test_callback)
    """
    return await _test_callback(callback, amount, payment_status)


async def _test_callback(model: YoomoneyCallbackModel, amount: float, payment_status: bool) -> Any:
    async with aiohttp.ClientSession() as session:
        if payment_status:
            unaccepted = 'false'
        elif not payment_status:
            unaccepted = 'true'
        amount_str = str(amount)
        data = {
            'operation_id': model.operation_id,
            'operation_label': model.operation_label,
            'notification_type': model.notification_type,
            'sender': model.sender,
            'firstname': model.firstname,
            'lastname': model.lastname,
            'fathername': model.fathername,
            'zip': model.zip,
            'city': model.city,
            'street': model.street,
            'building': model.building,
            'flat': model.flat,
            'suite': model.suite,
            'phone': model.phone,
            'email': model.email,
            'label': model.label,
            'codepro': model.codepro,
            'bill_id': model.bill_id,
            'amount': amount_str,
            'withdraw_amount': model.withdraw_amount,
            'currency': model.currency,
            'datetime': model.datetime,
            'unaccepted': unaccepted,
            'sha1_hash': model.sha1_hash
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
        }
        response = await session.post(
            url='http://localhost:8000/payment/api/v1/yoomoney/_callback',
            data=urlencode(data),
            headers=headers)
        return await response.json()
