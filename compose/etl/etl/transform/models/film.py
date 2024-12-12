from __future__ import annotations

from .base import (
    Document,
    DocumentRelation,
)


class Film(Document):
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


class FilmGenre(DocumentRelation):
    name: str


class FilmPerson(DocumentRelation):
    name: str


class FilmDirector(FilmPerson):
    pass


class FilmActor(FilmPerson):
    pass


class FilmWriter(FilmPerson):
    pass
