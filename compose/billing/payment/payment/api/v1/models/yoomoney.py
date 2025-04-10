from pydantic import BaseModel

class YoomoneyUserModel(BaseModel):
    user_id: str


class YoomoneyCallbackModel(BaseModel):
    code: str
    state: str
    
    
class YoomoneyPaymentModel(YoomoneyUserModel):
    pass