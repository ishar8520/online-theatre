import uuid

from typing import List
from pydantic import BaseModel


class PersonMixin:
    id: uuid.UUID
    name: str


class Director(BaseModel, PersonMixin):
    pass


class Actor(BaseModel, PersonMixin):
    pass


class Writer(BaseModel, PersonMixin):
    pass


class Genre(BaseModel):
    id: uuid.UUID
    name: str


class FilmInfo(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    # @todo TMP solution
    # genre: List[Genre]
    directors: List[Director] | None
    actors: List[Actor] | None
    writers: List[Writer] | None


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: float
