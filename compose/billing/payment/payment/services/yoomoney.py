from urllib.parse import urlencode
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from aio_pika import Message
import json
from http import HTTPStatus
import secrets
import requests

from payment.api.v1.models.yoomoney import YoomoneyPaymentModel
from payment.core.config import settings
from payment.services.rabbitmq import rabbitmq
from payment.services.redis import RedisClient

async def get_payment(model: YoomoneyPaymentModel, redis_client: RedisClient):
    if not await redis_client.get_value(f'yoomoney:payment:{model.user_id}'):
        params = {
            'pattern_id': model.pattern_id,
            'to': model.to,
            'amount': model.amount,
            'message': model.message,
            'label': model.label
        }
        await redis_client.set_value_with_ttl(
            key=f'yoomoney:payment:{model.user_id}',
            value=json.dumps(params),
            ttl_seconds=600)

    if not await redis_client.get_value(key=f'yoomoney:token:{model.user_id}'):
        return await get_auth_url(model.user_id, redis_client)
    return await get_payment_request(model.user_id, redis_client)


async def get_auth_url(user_id, redis_client):
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
    return {'url': f'https://yoomoney.ru/oauth/authorize?{urlencode(params)}'} 


async def get_auth_success(code: str, state:str, redis_client: RedisClient):
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


async def get_payment_request(user_id: str, redis_client: RedisClient):
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
    print('before request')
    response = requests.post(
        'https://yoomoney.ru/api/request-payment',
        headers=headers,
        data=data
    )
    response = response.json()
    print(response)
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
        accept_url = f'http://localhost:8000/payment/api/v1/yoomoney/_accept_payment/{response["request_id"]}'
        return {'accept_url': accept_url}
    return response


async def get_payment_accept(request_id, redis_client: RedisClient):
    print('start_accept')
    request_data = await redis_client.get_value(key=f'yoomoney:request_id:{request_id}')
    request_data = request_data.decode('utf-8')
    request_data = json.loads(request_data)
    await redis_client.delete_value(f'yoomoney:request_id:{request_id}')
    
    headers = {
        'Authorization': f'Bearer {request_data["token"]}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'request_id': request_data['request_id'],
        # 'money_source': 'wallet' #request_data['money_source']
    }
    response = requests.post(
        'https://yoomoney.ru/api/process-payment',
        headers=headers,
        data=data
    )
    print('accept_success')
    return response.json()


async def get_callback(request: Request):
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


async def send_queue(message, queue_name):
    await rabbitmq.channel.declare_queue(
        name=queue_name,
        durable=True,
        auto_delete=False
    )
    await rabbitmq.channel.default_exchange.publish(
        Message(body=json.dumps(message).encode()),
        routing_key=queue_name
    )

# async def get_payment_url_old(model: YoomoneyPaymentModel):
#     params = {
#         'receiver': settings.yoomoney.receiver_account,
#         'quickpay-form': model.quickpay_form,
#         'targets': model.targets,
#         'paymentType': model.paymentType,
#         'sum': model.sum,
#         'label': model.label,
#         'successURL': settings.yoomoney.redirect_uri
#     }
#     payment_url = f'https://yoomoney.ru/quickpay/confirm.xml?{urlencode(params)}'
#     return JSONResponse({'payment_url': payment_url})