import aiohttp
from fastapi import APIRouter
from payment.api.v1.models.yoomoney import YoomoneyCallbackModel

router = APIRouter()

@router.post('/_test_callback_success')
async def test_callback_success(
    callback: YoomoneyCallbackModel
):
    return await _test_callback_success(callback)

@router.post('/_test_callback_failed')
async def test_callback_failed(
    callback: YoomoneyCallbackModel
):
    return await _test_callback_failed(callback)

async def _test_callback_success(model: YoomoneyCallbackModel):
    async with aiohttp.ClientSession() as session:
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
            'amount': model.amount,
            'withdraw_amount': model.withdraw_amount,
            'currency': model.currency,
            'datetime': model.datetime,
            'unaccepted': 'false',
            'sha1_hash': model.sha1_hash 
        } 
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
        }

        response = await session.post(
            url='http://localhost:8000/payment/api/v1/yoomoney/callback',
            data=data,
            headers=headers)
        response_data = await response.json()
        return response_data
    
async def _test_callback_failed(model: YoomoneyCallbackModel):
    async with aiohttp.ClientSession() as session:
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
            'amount': model.amount,
            'withdraw_amount': model.withdraw_amount,
            'currency': model.currency,
            'datetime': model.datetime,
            'unaccepted': 'true',
            'sha1_hash': model.sha1_hash 
        } 
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
        }

        response = await session.post(
            url='http://localhost:8000/payment/api/v1/yoomoney/callback',
            data=data,
            headers=headers)
        response_data = await response.json()
        return response_data
