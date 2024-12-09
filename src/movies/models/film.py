from __future__ import annotations

import uuid
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
    title: str


class Film(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    imdb_rating: float
    # @todo TMP
    # genres: list[Genre]
    directors: list[Director] | None
    actors: list[Actor] | None
    writers: list[Writer] | None
