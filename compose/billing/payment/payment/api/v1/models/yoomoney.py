from pydantic import BaseModel
from datetime import datetime

class YoomoneyUserModel(BaseModel):
    user_id: str

# class YoomoneyPaymentModel(YoomoneyUserModel):
#     quickpay_form: str = 'small'
#     targets: str = 'Описание оплаты'
#     paymentType: str = 'AC'
#     sum: str = '100'
#     label: str = 'order_123'
class YoomoneyPaymentModel(YoomoneyUserModel):
    pattern_id: str='p2p'
    to: str
    amount: str='2.0'
    message: str='Оплата заказа #12345'
    label: str='order_12345'

class YoomoneyCallbackModel(BaseModel):
    operation_id: str
    operation_label: str
    notification_type: str
    sender: str = ''
    firstname: str = ''
    lastname: str = ''
    fathername: str = ''
    zip: str = ''
    city: str = ''
    street: str = ''
    building: str = ''
    flat: str = ''
    suite: str = ''
    phone: str = ''
    email: str = ''
    label: str
    codepro: str = 'false'
    bill_id: str = ''
    withdraw_amount: str
    currency: str
    datetime: datetime
    sha1_hash: str       
