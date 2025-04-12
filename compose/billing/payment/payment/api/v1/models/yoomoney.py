from pydantic import BaseModel

class YoomoneyUserModel(BaseModel):
    user_id: str

class YoomoneyPaymentModel(YoomoneyUserModel):
    quickpay_form: str = 'small'
    targets: str = 'Описание оплаты'
    paymentType: str = 'AC'
    sum: str = '100'
    label: str = 'order_123'
