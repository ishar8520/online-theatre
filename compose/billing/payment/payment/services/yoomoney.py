from urllib.parse import urlencode
from fastapi import Request

from payment.api.v1.models.yoomoney import YoomoneyPaymentModel
from payment.core.config import settings

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
    if data['unaccepted'] == 'false':
        status = 'success'
    else:
        status = 'failed'
    
    return {
        'label': data['label'],
        'amount': data['amount'],
        'withdraw_amount': data['withdraw_amount'],
        'datetime': data['datetime'],
        'status': status
    }
