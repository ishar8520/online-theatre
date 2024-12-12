from __future__ import annotations

import uuid
from pydantic import BaseModel, Field


class PersonMixin:
    id: uuid.UUID = Field(serialization_alias='uuid')
    name: str


class Director(BaseModel, PersonMixin):
    pass


class Actor(BaseModel, PersonMixin):
    pass


class Writer(BaseModel, PersonMixin):
    pass


class Genre(BaseModel):
    id: uuid.UUID = Field(serialization_alias='uuid')
    name: str


class Film(BaseModel):
    id: uuid.UUID = Field(serialization_alias='uuid')
    title: str
    description: str | None
    imdb_rating: float
    # @todo TMP
    # genres: list[Genre]
    directors: list[Director] | None
    actors: list[Actor] | None
    writers: list[Writer] | None
