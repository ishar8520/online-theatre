from urllib.parse import urlencode
from fastapi import Request, HTTPException
from aio_pika import Message
import json
from http import HTTPStatus


from payment.api.v1.models.yoomoney import YoomoneyPaymentModel
from payment.core.config import settings
from payment.services.rabbitmq import rabbitmq


async def queue_success(message, queue_name):
    queue = await rabbitmq.channel.declare_queue(
        name=queue_name,
        durable=True,
        auto_delete=False
    )
    await rabbitmq.channel.default_exchange.publish(
        Message(body=json.dumps(message).encode()),
        routing_key=queue_name,
    )

async def get_payment_url(model: YoomoneyPaymentModel):
    params = {
        'receiver': settings.yoomoney.receiver_account,
        'quickpay-form': model.quickpay_form,
        'targets': model.targets,
        'paymentType': model.paymentType,
        'sum': model.sum,
        'label': model.label,
        'successURL': settings.yoomoney.redirect_uri
    }
    payment_url = f'https://yoomoney.ru/quickpay/confirm.xml?{urlencode(params)}'
    return {'payment_url': payment_url}

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
        await queue_success(response, 'succeeded')
    elif data['unaccepted'] == 'true':
        response['status'] = 'failed'
        await queue_success(response, 'failed')
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Payment status undifined')
    return response
