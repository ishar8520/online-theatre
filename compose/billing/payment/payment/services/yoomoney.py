from urllib.parse import urlencode
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from aio_pika import Message
import json
from http import HTTPStatus
import secrets
from httpx import AsyncClient

from payment.api.v1.models.yoomoney import YoomoneyPaymentModel
from payment.core.config import settings
from payment.services.rabbitmq import rabbitmq
from payment.services.redis import RedisClient


base_service_url = settings.service.url


async def check_token(token: str, httpx_client: AsyncClient) -> dict:
    response = await httpx_client.get(
        'https://yoomoney.ru/api/account-info',
        headers={'Authorization': f'Bearer {token}'}
    )
    if response.status_code != HTTPStatus.OK:
        raise HTTPException(status_code=response.status_code)
    return response.json()


async def get_refund(user_id: str, model: YoomoneyPaymentModel, redis_client: RedisClient, httpx_client: AsyncClient) -> JSONResponse:
    if not await redis_client.get_value(f'yoomoney:refund:{user_id}'):
        params = {
            'pattern_id': model.pattern_id,
            'amount': str(model.amount),
            'message': model.message,
            'label': model.label
        }
        await redis_client.set_value_with_ttl(
            key=f'yoomoney:refund:{user_id}',
            value=json.dumps(params),
            ttl_seconds=600)
    if not await redis_client.get_value(key=f'yoomoney:token:{user_id}'):
        return await get_auth_url(user_id, 'refund', redis_client, httpx_client)
    return await get_refund_request(user_id, redis_client, httpx_client)

async def get_refund_request(user_id, redis_client, httpx_client):
    token = await redis_client.get_value(f'yoomoney:token:{user_id}')
    token = token.decode('utf-8')
    account_data = await check_token(token, httpx_client)
    
    account_token = settings.yoomoney.token_account
    
    refund_data = await redis_client.get_value(f'yoomoney:refund:{user_id}')
    refund_data = refund_data.decode('utf-8')
    await redis_client.delete_value(f'yoomoney:refund:{user_id}')
    data = json.loads(refund_data)
    data['to'] = account_data['account']
    headers = {
        'Authorization': f'Bearer {account_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = await httpx_client.post(
        'https://yoomoney.ru/api/request-payment',
        headers=headers,
        data=data
    )
    if response.status_code != HTTPStatus.OK:
        raise HTTPException(status_code=response.status_code)
    response = response.json()
    if response['status'] == 'success':
        request_data = {
            'request_id': response['request_id'],
            'money_source': response['money_source'],
            'token': token}
        await redis_client.set_value_with_ttl(
            key=f'yoomoney:request_id:{response["request_id"]}',
            value=json.dumps(request_data),
            ttl_seconds=600
        )
        accept_url = f'{base_service_url}/payment/api/v1/yoomoney/_accept_payment/{response["request_id"]}'
        data = {
            'user_id': user_id,
            'url': accept_url
        }
        response = await httpx_client.post(
            f'{settings.short_link.url}/short_link/shorten',
            data=data
        )
        response = response.json()
        
        return JSONResponse({'accept_url': response['short_url']})
    return JSONResponse(response)


async def get_payment(user_id: str, model: YoomoneyPaymentModel, redis_client: RedisClient, httpx_client: AsyncClient) -> JSONResponse:
    if not await redis_client.get_value(f'yoomoney:payment:{user_id}'):
        params = {
            'pattern_id': model.pattern_id,
            'to': settings.yoomoney.receiver_account,
            'amount': str(model.amount),
            'message': model.message,
            'label': model.label
        }
        await redis_client.set_value_with_ttl(
            key=f'yoomoney:payment:{user_id}',
            value=json.dumps(params),
            ttl_seconds=600)

    if not await redis_client.get_value(key=f'yoomoney:token:{user_id}'):
        return await get_auth_url(user_id, 'payment', redis_client, httpx_client)
    return await get_payment_request(user_id, redis_client, httpx_client)


async def get_auth_url(user_id: str, operation: str, redis_client: RedisClient, httpx_client: AsyncClient) -> JSONResponse:
    state = secrets.token_urlsafe(16)
    await redis_client.set_value_with_ttl(
        key=f'yoomoney:state:{state}',
        value=user_id,
        ttl_seconds=600
    )
    params = {
        'client_id': settings.yoomoney.client_id,
        'response_type': 'code',
        'redirect_uri': f'{settings.yoomoney.redirect_uri}?state={state}&operation={operation}',
        'scope': 'account-info payment-p2p',
        'state': state
    }
    data = {
        'user_id': user_id,
        'url': f'https://yoomoney.ru/oauth/authorize?{urlencode(params)}'
    }
    response = await httpx_client.post(
        f'{settings.short_link.url}/short_link/shorten',
        json=data
    )
    response = response.json()
    return JSONResponse({'url': response['short_url']})


async def get_auth_success(code: str, state: str, operation:str, redis_client: RedisClient, httpx_client: AsyncClient) -> JSONResponse:
    user_id = await redis_client.get_value(f'yoomoney:state:{state}')
    user_id = user_id.decode('utf-8')
    await redis_client.delete_value(f'yoomoney:state:{state}')
    response = await httpx_client.post(
        'https://yoomoney.ru/oauth/token',
        data={
            'code': code,
            'client_id': settings.yoomoney.client_id,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.yoomoney.redirect_uri,
            'client_secret': settings.yoomoney.secret,
        }
    )
    if response.status_code != HTTPStatus.OK:
        raise HTTPException(status_code=response.status_code)
    token = response.json().get('access_token')
    await redis_client.set_value_with_ttl(
        key=f'yoomoney:token:{user_id}',
        value=token,
        ttl_seconds=600
    )
    if operation == 'payment':
        return await get_payment_request(user_id, redis_client, httpx_client)
    elif operation == 'refund':
        return await get_refund_request(user_id, redis_client, httpx_client)


async def get_payment_request(user_id: str, redis_client: RedisClient, httpx_client: AsyncClient) -> JSONResponse:
    token = await redis_client.get_value(f'yoomoney:token:{user_id}')
    token = token.decode('utf-8')
    payment_data = await redis_client.get_value(f'yoomoney:payment:{user_id}')
    payment_data = payment_data.decode('utf-8')
    await redis_client.delete_value(f'yoomoney:payment:{user_id}')
    data = json.loads(payment_data)
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = await httpx_client.post(
        'https://yoomoney.ru/api/request-payment',
        headers=headers,
        data=data
    )
    if response.status_code != HTTPStatus.OK:
        raise HTTPException(status_code=response.status_code)
    response = response.json()
    if response['status'] == 'success':
        request_data = {
            'request_id': response['request_id'],
            'money_source': response['money_source'],
            'token': token}
        await redis_client.set_value_with_ttl(
            key=f'yoomoney:request_id:{response["request_id"]}',
            value=json.dumps(request_data),
            ttl_seconds=600
        )
        accept_url = f'{base_service_url}/payment/api/v1/yoomoney/_accept_payment/{response["request_id"]}'
        data = {
            'user_id': user_id,
            'url': accept_url
        }
        response = await httpx_client.post(
            f'{settings.short_link.url}/short_link/shorten',
            data=data
        )
        response = response.json()
        
        return JSONResponse({'accept_url': response['short_url']})
    return JSONResponse(response)


async def get_payment_accept(request_id, redis_client: RedisClient, httpx_client: AsyncClient) -> JSONResponse:
    request_data = await redis_client.get_value(key=f'yoomoney:request_id:{request_id}')
    request_data = request_data.decode('utf-8')
    request_data = json.loads(request_data)
    await redis_client.delete_value(f'yoomoney:request_id:{request_id}')
    
    headers = {
        'Authorization': f'Bearer {request_data["token"]}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'request_id': request_data['request_id']
    }
    response = await httpx_client.post(
        'https://yoomoney.ru/api/process-payment',
        headers=headers,
        data=data
    )
    if response.status_code != HTTPStatus.OK:
        raise HTTPException(status_code=response.status_code)
    return JSONResponse(response.json())


async def get_callback(request: Request) -> JSONResponse:
    data = await request.form()
    data = dict(data)
    response = {
        'label': data['label'],
        'amount': data['amount'],
        'withdraw_amount': data['withdraw_amount'],
        'datetime': data['datetime']
    }
    if data['unaccepted'] == 'false':
        response['status'] = 'success'
        await send_queue(response, 'succeeded')
    elif data['unaccepted'] == 'true':
        response['status'] = 'failed'
        await send_queue(response, 'failed')
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Payment status undifined')
    return JSONResponse(response)


async def send_queue(message, queue_name) -> None:
    await rabbitmq.channel.declare_queue(
        name=queue_name,
        durable=True,
        auto_delete=False
    )
    await rabbitmq.channel.default_exchange.publish(
        Message(body=json.dumps(message).encode()),
        routing_key=queue_name
    )
