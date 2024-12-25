import uuid

from pydantic import BaseModel


class FilmPerson(BaseModel):
    id: uuid.UUID
    roles: list[str]


class Person(BaseModel):
    id: uuid.UUID
    full_name: str
    films: list[FilmPerson] = []
