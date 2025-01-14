from . import *

class UserBase(BaseModel):
    id: UUID
    login: str
    first_name: str
    last_name: Optional[str]
    created: Optional[datetime]
    modified: Optional[datetime]

class UserCreate(BaseModel):
    login: str
    password: str
    first_name: str
    last_name: Optional[str]

class UserRead(UserBase):
    pass
