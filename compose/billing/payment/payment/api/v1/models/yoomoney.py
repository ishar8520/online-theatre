from pydantic import BaseModel

class YoomoneyUserModel(BaseModel):
    user_id: str


class YoomoneyCallbackModel(BaseModel):
    code: str
    state: str
    
    
class YoomoneyPaymentModel(YoomoneyUserModel):
    pattern_id: str='p2p'
    to: str='4100119088774786'
    amount: str='150.50'
    message: str='Оплата заказа #12345'
    label: str='order_12345'
    
# class YoomoneyAuthModel(BaseModel):
    