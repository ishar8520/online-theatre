from fastapi import APIRouter, HTTPException, Query, Depends
from urllib.parse import urlencode
import json
from http import HTTPStatus

from payment.core.config import settings
from payment.api.v1.models.yoomoney import YoomoneyPaymentModel
from payment.database.redis import get_redis_client, RedisClient
from payment.services.yoomoney import get_payment_url, get_callback

router = APIRouter()


@router.post('/payment')
async def payment(
    model: YoomoneyPaymentModel,
    redis_client: RedisClient = Depends(get_redis_client)
):
    try:
        response = await get_payment_url(model, redis_client)
        response = json.loads(response)
        if 'error' in response:
            print(response['error'])
            raise Exception(response['error'])
        
    except Exception as error:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error)
    return response
    

@router.get('/_callback')
async def callback(
    code: str = Query(...),
    state: str = Query(...),
    redis_client: RedisClient = Depends(get_redis_client)
):
    return await get_callback(code, state, redis_client)

@router.get('/webhook')
async def webhook():
    pass