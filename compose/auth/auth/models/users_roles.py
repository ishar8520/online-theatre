from . import *

class UserRoleBase(BaseModel):
    id: UUID
    user_id: UUID
    role_id: UUID
    created: Optional[datetime]

class UserRoleCreate(BaseModel):
    user_id: UUID
    role_id: UUID

class UserRoleRead(UserRoleBase):
    pass