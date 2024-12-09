from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel


class Film(BaseModel):
    id: str
    title: str
    description: Optional[str]
    imdb_rating: float
    directors: Optional[List]
    actors: Optional[List]
    writers: Optional[List]
