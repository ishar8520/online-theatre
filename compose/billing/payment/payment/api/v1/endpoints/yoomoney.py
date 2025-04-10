from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse, JSONResponse
import requests
from typing import Optional
from urllib.parse import urlencode
import secrets

from payment.core.config import settings
from payment.api.v1.models.yoomoney import YoomoneyUserModel, YoomoneyCallbackModel,  YoomoneyPaymentModel
from payment.database.redis import get_redis_client, RedisClient


router = APIRouter()


@router.get('/get_payment_url')
async def pay(user_id: str, redis_client: RedisClient = Depends(get_redis_client)):
    token = await redis_client.get_value(key=f'yoomoney:token:{user_id}')
    if token == None:
        params = {
            'user_id': user_id
        }
        return RedirectResponse(url=f'http://localhost:8000/payment/api/v1/yoomoney/auth?{urlencode(params)}')
    return RedirectResponse(url='http://localhost:8000/payment/api/v1/yoomoney/pay')

@router.get('/auth')
async def auth(user_id: str, redis_client: RedisClient = Depends(get_redis_client)):
    state = secrets.token_urlsafe(16)
    await redis_client.set_value_with_ttl(
        key=f'yoomoney:state:{state}',
        value=user_id,
        ttl_seconds=600
    )
    params = {
        'client_id': settings.yoomoney.client_id,
        'response_type': 'code',
        'redirect_uri': f'{settings.yoomoney.redirect_uri}?state={state}',
        'scope': 'account-info payment-p2p',
        'state': state
    }
    auth_url = f'https://yoomoney.ru/oauth/authorize?{urlencode(params)}'
    return {'auth_url': auth_url}


@router.get('/callback')
async def callback(
    code: str = Query(...),
    state: str = Query(...),
    redis_client: RedisClient = Depends(get_redis_client)
):
    user_id = await redis_client.get_value(f'yoomoney:state:{state}')
    await redis_client.delete_value(f'yoomoney:state:{state}')
    
    response = requests.post(
        'https://yoomoney.ru/oauth/token',
        data={
            'code': code,
            'client_id': settings.yoomoney.client_id,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.yoomoney.redirect_uri,
            'client_secret': settings.yoomoney.secret,
        }
    )
    token = response.json().get('access_token')
    
    await redis_client.set_value_with_ttl(
        key=f'yoomoney:token:{user_id.decode('utf-8')}',
        value=token,
        ttl_seconds=3600
    )
    return {'token': token}

@router.get('/pay')
async def pay():
    return {'WOW':'OWO'}