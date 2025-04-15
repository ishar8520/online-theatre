from pydantic import BaseModel
from datetime import datetime

class YoomoneyUserModel(BaseModel):
    user_id: str

class YoomoneyPaymentModel(YoomoneyUserModel):
    quickpay_form: str = 'small'
    targets: str = 'Описание оплаты'
    paymentType: str = 'AC'
    sum: str = '100'
    label: str = 'order_123'

class YoomoneyCallbackModel(BaseModel):
    operation_id: str = '797717204247227112'
    operation_label: str = '2f8b89f4-0011-5000-9000-13acc4aeffe3'
    notification_type: str = 'card-incoming'
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
    amount: str
    withdraw_amount: str
    currency: str = '643'
    
    datetime: datetime
    unaccepted: str = 'false'
    sha1_hash: str = '778ad2a8eff635eb879a59d59a0cff3cc9d1e28f'       
