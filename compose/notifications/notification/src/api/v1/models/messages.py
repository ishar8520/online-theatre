from __future__ import annotations

from pydantic import BaseModel


class MessageBase(BaseModel):
    subject: str
    template_id: str
    text: str
    type: str


class MessageBroadcastDto(MessageBase):
    pass


class MessagePersonalizedDto(MessageBase):
    pass
