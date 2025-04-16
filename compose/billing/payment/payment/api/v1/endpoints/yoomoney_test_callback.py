import aiohttp
from fastapi import APIRouter
from urllib.parse import urlencode
from payment.api.v1.models.yoomoney import YoomoneyCallbackModel

router = APIRouter()

@router.post('/_test_callback')
async def test_callback_success(
    callback: YoomoneyCallbackModel,
    amount: float,
    payment_status: bool
):
    return await _test_callback(callback, amount, payment_status)


async def _test_callback(model: YoomoneyCallbackModel, amount: float, payment_status: bool):
    async with aiohttp.ClientSession() as session:
        if payment_status == True:
            unaccepted = 'false'
        elif payment_status == False:
            unaccepted = 'true'
        amount = str(amount)
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
            'amount': amount,
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
            url='http://localhost:8000/payment/api/v1/yoomoney/callback',
            data=urlencode(data),
            headers=headers)
        return await response.json()
