from fastapi import APIRouter, Request, Depends, Query

from payment.api.v1.models.yoomoney import YoomoneyPaymentModel
from payment.services.yoomoney import get_payment, get_callback, get_auth_success, get_payment_accept
from payment.services.redis import RedisClient, get_redis_client

router = APIRouter()


# @router.post('/payment')
# async def payment(
#     model: YoomoneyPaymentModel
# ):
#     return await get_payment_url_old(model)

@router.post('/payment')
async def payment(
    model: YoomoneyPaymentModel,
    # user_id: str, 
    # amount: float,
    # label: str,
    redis_client: RedisClient = Depends(get_redis_client)
):
    return await get_payment(model, redis_client)

@router.post('/_callback')
async def callback(
    request: Request
):
    return await get_callback(request)

@router.get('/_auth_success')
async def auth_success(
    code: str = Query(...),
    state: str = Query(...),
    redis_client: RedisClient = Depends(get_redis_client)
):
    return await get_auth_success(code, state, redis_client)

@router.get('/_accept_payment/{request_id}')
async def accept_payment(
    request_id: str,
    redis_client: RedisClient = Depends(get_redis_client)
):
    return await get_payment_accept(request_id, redis_client)