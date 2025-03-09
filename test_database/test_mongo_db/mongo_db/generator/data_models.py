from datetime import datetime
from pydantic import BaseModel


class Like(BaseModel):
    user_id: str
    movie_id: str
    rating: int
    created_at: datetime


class Review(BaseModel):
    user_id: str
    movie_id: str
    rating: int
    text: str
    review_likes: int
    created_at: datetime


class Bookmark(BaseModel):
    user_id: str
    movie_id: str
    created_at: datetime
