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
