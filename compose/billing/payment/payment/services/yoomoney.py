import json
import secrets
from http import HTTPStatus
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

from aio_pika import Message
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from httpx import AsyncClient

from payment.api.v1.models.yoomoney import YoomoneyPaymentModel
from payment.core.config import settings
from payment.services.rabbitmq import rabbitmq
from payment.services.redis import RedisClient

base_service_url = settings.service.url


async def check_token(token: str, httpx_client: AsyncClient) -> dict[str, Any]:
    """
    Проверяет валидность токена через запрос к YooMoney API.

    :param token: Токен авторизации YooMoney
    :param httpx_client: Асинхронный HTTP-клиент
    :return: JSON с информацией об аккаунте
    """
    response = await httpx_client.get(
        'https://yoomoney.ru/api/account-info',
        headers={'Authorization': f'Bearer {token}'}
    )
    if response.status_code != HTTPStatus.OK:
        raise HTTPException(status_code=response.status_code)
    data: dict[str, Any] = response.json()
    return data


async def get_refund(
    user_id: UUID,
    model: YoomoneyPaymentModel,
    redis_client: RedisClient,
    httpx_client: AsyncClient
) -> JSONResponse:
    """
    Инициирует процесс возврата платежа через YooMoney.

    :param user_id: UUID пользователя в системе
    :param model: Данные о платеже для возврата
    :param redis_client: Клиент Redis для кеширования
    :param httpx_client: Асинхронный HTTP-клиент
    :return: JSONResponse со ссылкой для подтверждения или статусом операции
    """
    if not await redis_client.get_value(f'yoomoney:refund:{user_id}'):
        params = {
            'pattern_id': 'p2p',
            'amount': str(model.amount),
            'message': model.message,
            'label': model.label
        }
        await redis_client.set_value_with_ttl(
            key=f'yoomoney:refund:{user_id}',
            value=json.dumps(params),
            ttl_seconds=600)
    if not await redis_client.get_value(key=f'yoomoney:token:{user_id}'):
        return await get_auth_url(str(user_id), 'refund', redis_client, httpx_client)
    return await get_refund_request(user_id, redis_client, httpx_client)


async def get_refund_request(user_id: UUID, redis_client: RedisClient, httpx_client: AsyncClient) -> JSONResponse:
    """
    Выполняет запрос возврата платежа на YooMoney с предварительно сохранёнными данными.

    :param user_id: UUID пользователя
    :param redis_client: Клиент Redis
    :param httpx_client: Асинхронный HTTP-клиент
    :return: JSONResponse с результатом запроса возврата
    """
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
    response_json: dict[str, Any] = response.json()
    if response_json['status'] == 'success':
        request_data = {
            'request_id': response_json['request_id'],
            'money_source': response_json['money_source'],
            'token': token}
        await redis_client.set_value_with_ttl(
            key=f'yoomoney:request_id:{response_json["request_id"]}',
            value=json.dumps(request_data),
            ttl_seconds=600
        )
        accept_url = f'{base_service_url}/payment/api/v1/yoomoney/_accept_payment/{response_json["request_id"]}'
        data = {
            'user_id': str(user_id),
            'url': accept_url
        }
        shorten_response = await httpx_client.post(
            f'http://{settings.short_link.host}:{settings.short_link.port}/short_link/shorten',
            json=data
        )
        shortened_data: dict[str, Any] = shorten_response.json()

        return JSONResponse({'accept_url': shortened_data['short_url']})
    return JSONResponse(response_json)


async def get_payment(
    user_id: UUID,
    model: YoomoneyPaymentModel,
    redis_client: RedisClient,
    httpx_client: AsyncClient
) -> JSONResponse:
    """
    Инициирует платёж через YooMoney.

    :param user_id: UUID пользователя
    :param model: Данные платежа
    :param redis_client: Клиент Redis
    :param httpx_client: Асинхронный HTTP-клиент
    :return: JSONResponse со ссылкой на подтверждение платежа
    """
    if not await redis_client.get_value(f'yoomoney:payment:{user_id}'):
        params = {
            'pattern_id': 'p2p',
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
        return await get_auth_url(str(user_id), 'payment', redis_client, httpx_client)
    return await get_payment_request(str(user_id), redis_client, httpx_client)


async def get_auth_url(
        user_id: str, operation: str, redis_client: RedisClient, httpx_client: AsyncClient
) -> JSONResponse:
    """
    Создаёт и возвращает короткую ссылку для авторизации через YooMoney.

    :param user_id: ID пользователя
    :param operation: Операция после авторизации ('payment' или 'refund')
    :param redis_client: Клиент Redis
    :param httpx_client: Асинхронный HTTP-клиент
    :return: JSONResponse с сокращённой ссылкой авторизации
    """
    state = secrets.token_urlsafe(16)
    await redis_client.set_value_with_ttl(
        key=f'yoomoney:state:{state}',
        value=str(user_id),
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
        'user_id': str(user_id),
        'url': f'https://yoomoney.ru/oauth/authorize?{urlencode(params)}'
    }
    response = await httpx_client.post(
        f'http://{settings.short_link.host}:{settings.short_link.port}/short_link/shorten',
        json=data
    )

    response_data: dict[str, Any] = response.json()

    return JSONResponse({'url': response_data['short_url']})


async def get_auth_success(
        code: str, state: str, operation: str, redis_client: RedisClient, httpx_client: AsyncClient
) -> JSONResponse:
    """
    Обрабатывает успешную авторизацию и сохраняет токен YooMoney.

    :param code: Код авторизации от YooMoney
    :param state: Состояние, идентифицирующее пользователя
    :param operation: Операция после авторизации ('payment' или 'refund')
    :param redis_client: Клиент Redis
    :param httpx_client: Асинхронный HTTP-клиент
    :return: JSONResponse с результатом следующей операции
    """
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
    else:
        raise HTTPException(status_code=400, detail='Unknown operation type')


async def get_payment_request(
    user_id: str,
    redis_client: RedisClient,
    httpx_client: AsyncClient
) -> JSONResponse:
    """
    Отправляет запрос на выполнение платежа в YooMoney с ранее сохранёнными параметрами.

    :param user_id: ID пользователя
    :param redis_client: Клиент Redis
    :param httpx_client: Асинхронный HTTP-клиент
    :return: JSONResponse с результатом запроса платежа
    """
    token_bytes = await redis_client.get_value(f'yoomoney:token:{user_id}')
    token = token_bytes.decode('utf-8') if token_bytes else ''

    payment_data_bytes = await redis_client.get_value(f'yoomoney:payment:{user_id}')
    if payment_data_bytes is None:
        raise HTTPException(status_code=400, detail='Payment data not found')
    payment_data_str = payment_data_bytes.decode('utf-8')

    await redis_client.delete_value(f'yoomoney:payment:{user_id}')
    data = json.loads(payment_data_str)

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    payment_response = await httpx_client.post(
        'https://yoomoney.ru/api/request-payment',
        headers=headers,
        data=data
    )

    if payment_response.status_code != HTTPStatus.OK:
        raise HTTPException(status_code=payment_response.status_code)

    payment_json: dict[str, Any] = payment_response.json()

    if payment_json['status'] == 'success':
        request_data = {
            'request_id': payment_json['request_id'],
            'money_source': payment_json['money_source'],
            'token': token
        }

        await redis_client.set_value_with_ttl(
            key=f'yoomoney:request_id:{payment_json["request_id"]}',
            value=json.dumps(request_data),
            ttl_seconds=600
        )

        accept_url = (
            f'{base_service_url}/payment/api/v1/yoomoney/_accept_payment/{payment_json["request_id"]}'
        )
        shorten_payload = {
            'user_id': str(user_id),
            'url': accept_url
        }

        short_response = await httpx_client.post(
            f'http://{settings.short_link.host}:{settings.short_link.port}/short_link/shorten',
            json=shorten_payload
        )
        short_data: dict[str, Any] = short_response.json()

        return JSONResponse({'accept_url': short_data['short_url']})

    return JSONResponse(payment_json)


async def get_payment_accept(request_id: str, redis_client: RedisClient, httpx_client: AsyncClient) -> JSONResponse:
    """
    Подтверждает выполнение ранее созданного платежа в YooMoney.

    :param request_id: Идентификатор запроса платежа
    :param redis_client: Клиент Redis
    :param httpx_client: Асинхронный HTTP-клиент
    :return: JSONResponse с результатом подтверждения платежа
    """
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
    """
    Обрабатывает callback от YooMoney о статусе платежа.

    :param request: Запрос от YooMoney
    :return: JSONResponse с результатом обработки callback
    """
    form_data = await request.form()
    data: dict[str, Any] = dict(form_data)
    if not data:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Request body is empty')
    response = {
        'service': 'yoomoney',
        'label': data['label'],
        'amount': data['amount'],
        'withdraw_amount': data['withdraw_amount'],
        'datetime': data['datetime']
    }
    if data['unaccepted'] == 'false':
        response['status'] = 'success'
        await send_queue(response, 'status_queue')
    elif data['unaccepted'] == 'true':
        response['status'] = 'failed'
        await send_queue(response, 'status_queue')
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Payment status undifined')
    return JSONResponse(response)


async def send_queue(message: dict[str, Any], queue_name: str) -> None:
    """
    Отправляет сообщение в очередь RabbitMQ.

    :param message: Сообщение для отправки
    :param queue_name: Имя очереди для отправки сообщения
    """
    if rabbitmq.channel is None:
        raise RuntimeError("RabbitMQ channel is not initialized")

    await rabbitmq.channel.declare_queue(
        name=queue_name,
        durable=True,
        auto_delete=False
    )

    await rabbitmq.channel.default_exchange.publish(
        Message(body=json.dumps(message).encode()),
        routing_key=queue_name
    )
