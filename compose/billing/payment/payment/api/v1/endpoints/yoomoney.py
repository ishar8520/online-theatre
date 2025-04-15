from fastapi import APIRouter, Request

from payment.api.v1.models.yoomoney import YoomoneyPaymentModel
from payment.services.yoomoney import get_payment_url, get_callback

router = APIRouter()


@router.post('/payment')
async def payment(
    model: YoomoneyPaymentModel,
):
    return await get_payment_url(model)
    

@router.post('/callback')
async def callback(
    request: Request
):
    return await get_callback(request)



    # FormData([('notification_type', 'card-incoming'), 
    # ('zip', ''), ('bill_id', ''), ('amount', '1.94'), 
    # ('firstname', ''), ('codepro', 'false'), ('withdraw_amount', '2.00'), 
    # ('city', ''), ('unaccepted', 'false'), ('label', '12345'), 
    # ('building', ''), ('lastname', ''), ('datetime', '2025-04-11T20:06:44Z'), 
    # ('suite', ''), ('sender', ''), ('phone', ''), 
    # ('sha1_hash', '778ad2a8eff635eb879a59d59a0cff3cc9d1e28f'), 
    # ('street', ''), ('flat', ''), ('fathersname', ''), 
    # ('operation_label', '2f8b89f4-0011-5000-9000-13acc4aeffe3'), 
    # ('operation_id', '797717204247227112'), ('currency', '643'), 
    # ('email', '')])
