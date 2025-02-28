from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Like(BaseModel):
    user_id: UUID
    movie_id: str
    rating: int
    timestamp: datetime


class Review(BaseModel):
    user_id: UUID
    movie_id: str
    rating: int
    text: str
    review_likes: int
    timestamp: datetime


class Bookmark(BaseModel):
    user_id: int
    movie_id: int
    timestamp: datetime
