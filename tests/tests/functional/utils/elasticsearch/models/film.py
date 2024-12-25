import uuid

from pydantic import BaseModel, computed_field


class Person(BaseModel):
    id: uuid.UUID
    full_name: str


class Actor(Person):
    pass


class Director(Person):
    pass


class Writer(Person):
    pass


class Genre(BaseModel):
    id: uuid.UUID
    name: str


class Film(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    rating: float
    actors: list[Actor] = []
    genres: list[Genre] = []
    directors: list[Director] = []
    writers: list[Writer] = []

    @computed_field
    def actors_names(self) -> list[str]:
        return [person.full_name for person in self.actors]

    @computed_field
    def genres_names(self) -> list[str]:
        return [item.name for item in self.genres]

    @computed_field
    def directors_names(self) -> list[str]:
        return [person.full_name for person in self.directors]

    @computed_field
    def writers_names(self) -> list[str]:
        return [person.full_name for person in self.writers]
