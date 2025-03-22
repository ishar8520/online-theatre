from uuid import UUID

from pydantic import BaseModel


class ShortenResponse(BaseModel):
    short_url: str


class ShortenRequest(BaseModel):
    user_id: UUID
    url: str
