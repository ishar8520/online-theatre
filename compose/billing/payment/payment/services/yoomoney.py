import secrets
import json
from fastapi import Depends
from fastapi.responses import RedirectResponse, JSONResponse
from urllib.parse import urlencode
import requests

from payment.api.v1.models.yoomoney import YoomoneyPaymentModel
from payment.database.redis import RedisClient
from payment.core.config import settings

async def get_payment_url(
    model: YoomoneyPaymentModel,
    redis_client: RedisClient
):
    if not await redis_client.get_value(f'yoomoney:payment:{model.user_id}'):
        params = {
            'pattern_id': model.pattern_id,
            'to': model.to,
            'amount': model.amount,
            'message': model.message,
            'label': model.label
        }
        # params = '|'.join([model.pattern_id, model.to, model.amount, model.message, model.label])
        await redis_client.set_value_with_ttl(
            key=f'yoomoney:payment:{model.user_id}',
            value=json.dumps(params),
            ttl_seconds=3600)

    if not await redis_client.get_value(key=f'yoomoney:token:{model.user_id}'):
        return await get_auth(model.user_id, redis_client)
    return await payment(model.user_id, redis_client)
    
async def get_auth(
    user_id: str,
    redis_client
):
    state = secrets.token_urlsafe(16)
    await redis_client.set_value_with_ttl(
            key=f'yoomoney:state:{state}',
            value=user_id,
            ttl_seconds=3600)
    params = {
        'client_id': settings.yoomoney.client_id,
        'response_type': 'code',
        'redirect_uri': f'{settings.yoomoney.redirect_uri}?state={state}',
        'scope': 'account-info payment-p2p',
        'state': state
    }
    auth_url = f'https://yoomoney.ru/oauth/authorize?{urlencode(params)}'
    return JSONResponse({'auth_url': auth_url})

async def get_callback(
    code: str,
    state: str,
    redis_client: RedisClient
):
    user_id = await redis_client.get_value(f'yoomoney:state:{state}')
    user_id = user_id.decode('utf-8')
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
        key=f'yoomoney:token:{user_id}',
        value=token,
        ttl_seconds=3600
    )
    return await payment(user_id, redis_client)

async def payment(user_id: str, redis_client):
    token = await redis_client.get_value(f'yoomoney:token:{user_id}')
    token = token.decode('utf-8')
    payment_data = await redis_client.get_value(f'yoomoney:payment:{user_id}')
    payment_data = payment_data.decode('utf-8')
    print(payment_data)
    data = json.loads(payment_data)
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(
        'https://yoomoney.ru/api/request-payment',
        headers=headers,
        data=data
    )
    response.raise_for_status()
    return response.json()
