from __future__ import annotations

import uuid

from pydantic import BaseModel


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


class FilmGenre(BaseModel):
    id: uuid.UUID
    name: str


class FilmPerson(BaseModel):
    id: uuid.UUID
    name: str


class FilmDirector(FilmPerson):
    pass


class FilmActor(FilmPerson):
    pass


class FilmWriter(FilmPerson):
    pass
