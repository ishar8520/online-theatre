from fastapi import APIRouter, Request, Depends, Query

from payment.api.v1.models.yoomoney import YoomoneyPaymentModel, YoomoneyRefundModel
from payment.services.yoomoney import (
    get_payment,
    get_refund,
    get_callback,
    get_auth_success,
    get_payment_accept,
    check_token
)
from payment.services.redis import RedisClient, get_redis_client

router_in = APIRouter()
router_ex = APIRouter()

@router_ex.get('/check')
async def check():
    return await check_token()

@router_ex.post('/payment')
async def payment(
    user_id: str,
    model: YoomoneyPaymentModel,
    redis_client: RedisClient = Depends(get_redis_client)
):
    return await get_payment(user_id, model, redis_client)

@router_ex.post('/refund')
async def refund(
    model: YoomoneyRefundModel,
    redis_client: RedisClient = Depends(get_redis_client)
):
    return await get_refund(model, redis_client)
    
@router_in.post('/_callback')
async def callback(
    request: Request
):
    return await get_callback(request)

@router_in.get('/_auth_success')
async def auth_success(
    code: str = Query(...),
    state: str = Query(...),
    redis_client: RedisClient = Depends(get_redis_client)
):
    return await get_auth_success(code, state, redis_client)

@router_in.get('/_accept_payment/{request_id}')
async def accept_payment(
    request_id: str,
    redis_client: RedisClient = Depends(get_redis_client)
):
    return await get_payment_accept(request_id, redis_client)
