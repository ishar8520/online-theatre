from __future__ import annotations

import uuid

from pydantic import (
    BaseModel,
    field_serializer,
    SerializationInfo,
)


class Film(BaseModel):
    id: uuid.UUID
    imdb_rating: float | None
    genres: list[str]
    title: str
    description: str | None
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    directors: list[FilmDirector]
    actors: list[FilmActor]
    writers: list[FilmWriter]

    @field_serializer('id')
    def serialize_id(self, value: uuid.UUID, _info: SerializationInfo) -> str:
        return str(value)


class FilmPerson(BaseModel):
    id: uuid.UUID
    name: str

    @field_serializer('id')
    def serialize_id(self, value: uuid.UUID, _info: SerializationInfo) -> str:
        return str(value)


class FilmDirector(FilmPerson):
    pass


class FilmActor(FilmPerson):
    pass


class FilmWriter(FilmPerson):
    pass
