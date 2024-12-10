from __future__ import annotations

from collections.abc import Iterable


class FilmWorksParser:
    film_works: Iterable[dict]

    def __init__(self, *, film_works: Iterable[dict]) -> None:
        self.film_works = film_works

    def parse(self, *, visitor: FilmWorksVisitor) -> None:
        for film_work_data in self.film_works:
            visitor.start_handle_film_work(film_work_data=film_work_data)

            for genre_data in film_work_data['genres']:
                visitor.handle_genre(genre_data=genre_data)

            for person_data in film_work_data['persons']:
                visitor.handle_person(person_data=person_data)

            visitor.end_handle_film_work(film_work_data=film_work_data)


class FilmWorksVisitor:
    def start_handle_film_work(self, *, film_work_data: dict) -> None:
        pass

    def end_handle_film_work(self, *, film_work_data: dict) -> None:
        pass

    def handle_genre(self, *, genre_data: dict) -> None:
        pass

    def handle_person(self, *, person_data: dict) -> None:
        pass
