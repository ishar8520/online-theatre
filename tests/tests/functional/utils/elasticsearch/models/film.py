from __future__ import annotations

from pydantic import computed_field

from .base import (
    Document,
    DocumentRelation,
)


class Film(Document):
    title: str
    description: str | None
    rating: float | None
    # noinspection PyDataclass
    genres: list[FilmGenre] = []
    # noinspection PyDataclass
    directors: list[FilmDirector] = []
    # noinspection PyDataclass
    actors: list[FilmActor] = []
    # noinspection PyDataclass
    writers: list[FilmWriter] = []

    @computed_field
    def genres_names(self) -> list[str]:
        return [genre.name for genre in self.genres]

    @computed_field
    def directors_names(self) -> list[str]:
        return [person.full_name for person in self.directors]

    @computed_field
    def actors_names(self) -> list[str]:
        return [person.full_name for person in self.actors]

    @computed_field
    def writers_names(self) -> list[str]:
        return [person.full_name for person in self.writers]


class FilmGenre(DocumentRelation):
    name: str


class FilmPerson(DocumentRelation):
    full_name: str


class FilmDirector(FilmPerson):
    pass


class FilmActor(FilmPerson):
    pass


class FilmWriter(FilmPerson):
    pass
