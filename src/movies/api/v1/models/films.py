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
    name: str


class FilmInfo(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    # @todo TMP solution
    # genre: list[Genre]
    directors: list[Director] | None
    actors: list[Actor] | None
    writers: list[Writer] | None


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: float
