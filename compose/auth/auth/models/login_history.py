from . import *

class LoginHistoryBase(BaseModel):
    id: UUID
    user_id: UUID
    user_agent: str
    created: Optional[datetime]

class LoginHistoryCreate(BaseModel):
    user_id: UUID
    user_agent: str

class LoginHistoryRead(LoginHistoryBase):
    pass