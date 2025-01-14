from . import *

class RoleBase(BaseModel):
    id: UUID
    name: str
    created: Optional[datetime]
    modified: Optional[datetime]

class RoleCreate(BaseModel):
    name: str

class RoleRead(RoleBase):
    pass
