from __future__ import annotations

import uuid

from pydantic import (
    BaseModel,
    field_serializer,
    SerializationInfo,
)


class Movie(BaseModel):
    id: uuid.UUID
    imdb_rating: float | None
    genres: list[str]
    title: str
    description: str | None
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    directors: list[Director]
    actors: list[Actor]
    writers: list[Writer]

    @field_serializer('id')
    def serialize_id(self, value: uuid.UUID, _info: SerializationInfo) -> str:
        return str(value)


class Person(BaseModel):
    id: uuid.UUID
    name: str

    @field_serializer('id')
    def serialize_id(self, value: uuid.UUID, _info: SerializationInfo) -> str:
        return str(value)


class Director(Person):
    pass


class Actor(Person):
    pass


class Writer(Person):
    pass
