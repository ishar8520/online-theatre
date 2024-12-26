from __future__ import annotations

from .base import (
    Document,
    DocumentRelation,
)


class Person(Document):
    full_name: str
    # noinspection PyDataclass
    films: list[PersonFilm] = []


class PersonFilm(DocumentRelation):
    # noinspection PyDataclass
    roles: list[str] = []
