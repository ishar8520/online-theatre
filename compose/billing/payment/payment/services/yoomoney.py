from urllib.parse import urlencode
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from aio_pika import Message
import json
from http import HTTPStatus
import secrets
import requests

from payment.api.v1.models.yoomoney import YoomoneyPaymentModel, YoomoneyRefundModel
from payment.core.config import settings
from payment.services.rabbitmq import rabbitmq
from payment.services.redis import RedisClient


base_service_url = settings.service.url

async def check_token():
    response = requests.get(
        "https://yoomoney.ru/api/account-info",
        headers={"Authorization": f"Bearer {settings.yoomoney.token_account}"}
    )
    return response

async def get_refund(model: YoomoneyRefundModel, redis_client: RedisClient) -> JSONResponse:
    token = settings.yoomoney.token_account
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = {
        'pattern_id': model.pattern_id,
        'to': model.to,
        'amount': str(model.amount),
        'message': model.message,
        'label': model.label
    }
    response = requests.post(
        'https://yoomoney.ru/api/request-payment',
        headers=headers,
        data=params
    )
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
        return JSONResponse({'accept_url': accept_url})
    return JSONResponse(response)

async def get_payment(user_id: str, model: YoomoneyPaymentModel, redis_client: RedisClient) -> JSONResponse:
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
        return await get_auth_url(user_id, redis_client)
    return await get_payment_request(user_id, redis_client)


async def get_auth_url(user_id: str, redis_client: RedisClient) -> JSONResponse:
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
    return JSONResponse({'url': f'https://yoomoney.ru/oauth/authorize?{urlencode(params)}'})


async def get_auth_success(code: str, state: str, redis_client: RedisClient) -> JSONResponse:
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
        ttl_seconds=600
    )
    return await get_payment_request(user_id, redis_client)


async def get_payment_request(user_id: str, redis_client: RedisClient) -> JSONResponse:
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
    response = requests.post(
        'https://yoomoney.ru/api/request-payment',
        headers=headers,
        data=data
    )
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
        return JSONResponse({'accept_url': accept_url})
    return JSONResponse(response)


async def get_payment_accept(request_id, redis_client: RedisClient) -> JSONResponse:
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
    response = requests.post(
        'https://yoomoney.ru/api/process-payment',
        headers=headers,
        data=data
    )
    return JSONResponse(response.json())


async def get_callback(request: Request) -> JSONResponse:
    data = await request.form()
    data = dict(data)
    response = {
        'label': data['label'],
        'amount': data['amount'],
        'withdraw_amount': data['withdraw_amount'],
        'datetime': data['datetime'],
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
