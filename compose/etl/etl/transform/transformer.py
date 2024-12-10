from __future__ import annotations

import dataclasses

from .serializers import (
    Movie,
    Director,
    Actor,
    Writer,
)
from ..extract import (
    FilmWorksVisitor,
    LastModified,
)


@dataclasses.dataclass(kw_only=True)
class MovieTransformState:
    genres: list[str] = dataclasses.field(default_factory=list)
    directors_names: list[str] = dataclasses.field(default_factory=list)
    actors_names: list[str] = dataclasses.field(default_factory=list)
    writers_names: list[str] = dataclasses.field(default_factory=list)
    directors: list[Director] = dataclasses.field(default_factory=list)
    actors: list[Actor] = dataclasses.field(default_factory=list)
    writers: list[Writer] = dataclasses.field(default_factory=list)

    def reset(self) -> None:
        self.genres = []
        self.directors_names = []
        self.actors_names = []
        self.writers_names = []
        self.directors = []
        self.actors = []
        self.writers = []


@dataclasses.dataclass(kw_only=True)
class MoviesTransformResult:
    movies: list[Movie] = dataclasses.field(default_factory=list)
    last_modified: LastModified = dataclasses.field(default_factory=lambda: LastModified())


class MoviesTransformer(FilmWorksVisitor):
    movie_state: MovieTransformState
    result: MoviesTransformResult

    def __init__(self) -> None:
        self.movie_state = MovieTransformState()
        self.result = MoviesTransformResult()

    def get_result(self) -> MoviesTransformResult:
        return self.result

    def start_handle_film_work(self, *, film_work_data: dict) -> None:
        self.movie_state.reset()

    def end_handle_film_work(self, *, film_work_data: dict) -> None:
        self.result.movies.append(Movie(
            id=film_work_data['id'],
            imdb_rating=film_work_data['rating'],
            genres=self.movie_state.genres,
            title=film_work_data['title'],
            description=film_work_data['description'],
            directors_names=self.movie_state.directors_names,
            actors_names=self.movie_state.actors_names,
            writers_names=self.movie_state.writers_names,
            directors=self.movie_state.directors,
            actors=self.movie_state.actors,
            writers=self.movie_state.writers,
        ))

        self.result.last_modified = LastModified(
            modified=film_work_data['modified'],
            id=film_work_data['id'],
        )

    def handle_genre(self, *, genre_data: dict) -> None:
        self.movie_state.genres.append(genre_data['name'])

    def handle_person(self, *, person_data: dict) -> None:
        if person_data['role'] == 'director':
            self.movie_state.directors_names.append(person_data['full_name'])
            self.movie_state.directors.append(Director(
                id=person_data['id'],
                name=person_data['full_name'],
            ))
            return

        if person_data['role'] == 'actor':
            self.movie_state.actors_names.append(person_data['full_name'])
            self.movie_state.actors.append(Actor(
                id=person_data['id'],
                name=person_data['full_name'],
            ))
            return

        if person_data['role'] == 'writer':
            self.movie_state.writers_names.append(person_data['full_name'])
            self.movie_state.writers.append(Writer(
                id=person_data['id'],
                name=person_data['full_name'],
            ))
