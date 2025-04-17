from fastapi import APIRouter, Request, Depends, Query
import httpx
from collections.abc import AsyncGenerator

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

async def get_httpx_client() -> AsyncGenerator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as client:
        yield client


@router_ex.get('/check')
async def check(
    httpx_client: httpx.AsyncClient = Depends(get_httpx_client)
):
    return await check_token(httpx_client)

@router_ex.post('/payment')
async def payment(
    user_id: str,
    model: YoomoneyPaymentModel,
    redis_client: RedisClient = Depends(get_redis_client),
    httpx_client: httpx.AsyncClient = Depends(get_httpx_client)
):
    return await get_payment(user_id, model, redis_client, httpx_client)

@router_ex.post('/refund')
async def refund(
    model: YoomoneyRefundModel,
    redis_client: RedisClient = Depends(get_redis_client),
    httpx_client: httpx.AsyncClient = Depends(get_httpx_client)
):
    return await get_refund(model, redis_client, httpx_client)
    
@router_in.post('/_callback')
async def callback(
    request: Request,
):
    return await get_callback(request)

@router_in.get('/_auth_success')
async def auth_success(
    code: str = Query(...),
    state: str = Query(...),
    redis_client: RedisClient = Depends(get_redis_client),
    httpx_client: httpx.AsyncClient = Depends(get_httpx_client)
):
    return await get_auth_success(code, state, redis_client, httpx_client)

@router_in.get('/_accept_payment/{request_id}')
async def accept_payment(
    request_id: str,
    redis_client: RedisClient = Depends(get_redis_client),
    httpx_client: httpx.AsyncClient = Depends(get_httpx_client)
):
    return await get_payment_accept(request_id, redis_client, httpx_client)
