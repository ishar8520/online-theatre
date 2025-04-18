from pydantic import BaseModel
from datetime import datetime

class YoomoneyUserModel(BaseModel):
    user_id: str

class YoomoneyPaymentModel(BaseModel):
    pattern_id: str='p2p'
    amount: float
    message: str
    label: str

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
