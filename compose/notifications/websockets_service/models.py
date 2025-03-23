from pydantic import BaseModel
from uuid import UUID

class MessageModel(BaseModel):
    user_uuid: UUID
    text: str
