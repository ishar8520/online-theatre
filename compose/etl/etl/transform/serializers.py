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
    title: str
    description: str | None
    genres_names: list[str]
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    genres: list[FilmGenre]
    directors: list[FilmDirector]
    actors: list[FilmActor]
    writers: list[FilmWriter]

    @field_serializer('id')
    def serialize_id(self, value: uuid.UUID, _info: SerializationInfo) -> str:
        return str(value)


class FilmGenre(BaseModel):
    id: uuid.UUID
    name: str

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
