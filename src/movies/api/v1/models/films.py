from __future__ import annotations

import uuid

from pydantic import BaseModel


class PersonMixin:
    uuid: uuid.UUID
    name: str


class Director(BaseModel, PersonMixin):
    pass


class Actor(BaseModel, PersonMixin):
    pass


class Writer(BaseModel, PersonMixin):
    pass


class Genre(BaseModel):
    uuid: uuid.UUID
    name: str


class FilmInfo(BaseModel):
    uuid: uuid.UUID
    title: str
    description: str
    # @todo TMP solution
    # genre: list[Genre]
    directors: list[Director] | None
    actors: list[Actor] | None
    writers: list[Writer] | None


class Film(BaseModel):
    uuid: uuid.UUID
    title: str
    imdb_rating: float
