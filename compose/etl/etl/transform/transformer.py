from __future__ import annotations

import dataclasses

from .serializers import (
    Film,
    FilmDirector,
    FilmActor,
    FilmWriter,
)
from ..extract import (
    FilmWorksVisitor,
    LastModified,
)


@dataclasses.dataclass(kw_only=True)
class FilmTransformState:
    genres: list[str] = dataclasses.field(default_factory=list)
    directors_names: list[str] = dataclasses.field(default_factory=list)
    actors_names: list[str] = dataclasses.field(default_factory=list)
    writers_names: list[str] = dataclasses.field(default_factory=list)
    directors: list[FilmDirector] = dataclasses.field(default_factory=list)
    actors: list[FilmActor] = dataclasses.field(default_factory=list)
    writers: list[FilmWriter] = dataclasses.field(default_factory=list)

    def reset(self) -> None:
        self.genres = []
        self.directors_names = []
        self.actors_names = []
        self.writers_names = []
        self.directors = []
        self.actors = []
        self.writers = []


@dataclasses.dataclass(kw_only=True)
class FilmsTransformResult:
    films: list[Film] = dataclasses.field(default_factory=list)
    last_modified: LastModified = dataclasses.field(default_factory=lambda: LastModified())


class FilmsTransformer(FilmWorksVisitor):
    film_state: FilmTransformState
    result: FilmsTransformResult

    def __init__(self) -> None:
        self.film_state = FilmTransformState()
        self.result = FilmsTransformResult()

    def get_result(self) -> FilmsTransformResult:
        return self.result

    def start_handle_film_work(self, *, film_work_data: dict) -> None:
        self.film_state.reset()

    def end_handle_film_work(self, *, film_work_data: dict) -> None:
        self.result.films.append(Film(
            id=film_work_data['id'],
            imdb_rating=film_work_data['rating'],
            genres=self.film_state.genres,
            title=film_work_data['title'],
            description=film_work_data['description'],
            directors_names=self.film_state.directors_names,
            actors_names=self.film_state.actors_names,
            writers_names=self.film_state.writers_names,
            directors=self.film_state.directors,
            actors=self.film_state.actors,
            writers=self.film_state.writers,
        ))

        self.result.last_modified = LastModified(
            modified=film_work_data['modified'],
            id=film_work_data['id'],
        )

    def handle_genre(self, *, genre_data: dict) -> None:
        self.film_state.genres.append(genre_data['name'])

    def handle_person(self, *, person_data: dict) -> None:
        if person_data['role'] == 'director':
            self.film_state.directors_names.append(person_data['full_name'])
            self.film_state.directors.append(FilmDirector(
                id=person_data['id'],
                name=person_data['full_name'],
            ))
            return

        if person_data['role'] == 'actor':
            self.film_state.actors_names.append(person_data['full_name'])
            self.film_state.actors.append(FilmActor(
                id=person_data['id'],
                name=person_data['full_name'],
            ))
            return

        if person_data['role'] == 'writer':
            self.film_state.writers_names.append(person_data['full_name'])
            self.film_state.writers.append(FilmWriter(
                id=person_data['id'],
                name=person_data['full_name'],
            ))
