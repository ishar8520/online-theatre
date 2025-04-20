import uuid
from collections.abc import AsyncGenerator
from typing import Any
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from payment.api.v1.models.yoomoney import YoomoneyPaymentModel
from payment.services.redis import RedisClient, get_redis_client
from payment.services.yoomoney import (
    check_token,
    get_auth_success,
    get_callback,
    get_payment,
    get_payment_accept,
    get_refund,
)

router_in = APIRouter()
router_ex = APIRouter()


async def get_httpx_client() -> AsyncGenerator[httpx.AsyncClient]:
    """
    Создаёт контекстный HTTPX-клиент для выполнения асинхронных HTTP‑запросов.

    После выхода из контекста клиент закрывается автоматически.
    """
    async with httpx.AsyncClient() as client:
        yield client


@router_ex.get('/check')
async def check(
    token: str,
    httpx_client: httpx.AsyncClient = Depends(get_httpx_client)
) -> dict[Any, Any]:
    """
    Проверяет статус платёжной операции в YooMoney.

    :param token: токен операции, полученный от клиента
    :param httpx_client: асинхронный HTTP‑клиент для запроса к API YooMoney
    :return: JSON с результатом проверки (успех/ошибка и детали)
    """
    return await check_token(token, httpx_client)


@router_ex.post('/payment/{user_id}')
async def payment(
    user_id: uuid.UUID,
    model: YoomoneyPaymentModel,
    redis_client: RedisClient = Depends(get_redis_client),
    httpx_client: httpx.AsyncClient = Depends(get_httpx_client)
) -> JSONResponse:
    """
    Инициализирует платёж через YooMoney.

    :param user_id: идентификатор пользователя в вашей системе
    :param model: модель данных платежа (сумма, валюта, описание и т.д.)
    :param redis_client: клиент Redis для получения или сохранения данных платежа
    :param httpx_client: асинхронный HTTP‑клиент для обращения к API YooMoney
    :return: JSON с результатом операции (успех/ошибка и детали)
    """
    return await get_payment(user_id, model, redis_client, httpx_client)


@router_ex.post('/refund/{user_id}')
async def refund(
    user_id: UUID,
    model: YoomoneyPaymentModel,
    redis_client: RedisClient = Depends(get_redis_client),
    httpx_client: httpx.AsyncClient = Depends(get_httpx_client)
) -> JSONResponse:
    """
    Создаёт запрос на возврат платежа через YooMoney.

    :param user_id: идентификатор пользователя в вашей системе
    :param model: модель данных с информацией о сумме и причине возврата
    :param redis_client: клиент Redis для получения или сохранения данных платежа
    :param httpx_client: асинхронный HTTP‑клиент для обращения к API YooMoney
    :return: JSON с результатами операции (успех, ошибка, детали)
    """
    return await get_refund(user_id, model, redis_client, httpx_client)


@router_in.post('/_callback')
async def callback(
    request: Request,
) -> JSONResponse:
    """
    Обрабатывает callback от YooMoney при изменении статуса платежа.

    :param request: экземпляр Request с данными от YooMoney
    :return: JSON-подтверждение приёма callback ({"status": "ok"})
    """
    return await get_callback(request)


@router_in.get('/_auth_success')
async def auth_success(
    code: str = Query(...),
    state: str = Query(...),
    operation: str = Query(...),
    redis_client: RedisClient = Depends(get_redis_client),
    httpx_client: httpx.AsyncClient = Depends(get_httpx_client)
) -> JSONResponse:
    """
    Обрабатывает успешную авторизацию пользователя через YooMoney.

    :param code: код авторизации, возвращённый YooMoney
    :param state: состояние (state), переданное при запуске OAuth‑процесса
    :param operation: тип операции, которую необходимо выполнить после авторизации (например, 'payment' или 'refund')
    :param redis_client: клиент Redis для получения или сохранения данных платежа
    :param httpx_client: асинхронный HTTP‑клиент для вызова внутренних или внешних HTTP‑эндпоинтов
    :return: перенаправление или JSON с информацией об успешной авторизации
    """
    return await get_auth_success(code, state, operation, redis_client, httpx_client)


@router_in.get('/_accept_payment/{request_id}')
async def accept_payment(
    request_id: str,
    redis_client: RedisClient = Depends(get_redis_client),
    httpx_client: httpx.AsyncClient = Depends(get_httpx_client)
) -> JSONResponse:
    """
    Обрабатывает подтверждение платежа в YooMoney по идентификатору запроса.

    :param request_id: уникальный идентификатор запроса на платёж
    :param redis_client: клиент Redis для получения или сохранения данных платежа
    :param httpx_client: асинхронный HTTP‑клиент для вызова внутренних или внешних HTTP‑эндпоинтов
    :return: JSON с результатом обработки (успешно/ошибка и детали)
    """
    return await get_payment_accept(request_id, redis_client, httpx_client)
