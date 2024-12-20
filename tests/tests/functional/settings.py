from __future__ import annotations

from urllib.parse import urljoin

from dotenv import load_dotenv
from pydantic import (
    Field,
    computed_field,
)
from pydantic_settings import (
    BaseSettings,
)

load_dotenv()


class Settings(BaseSettings):
    movies_url: str = Field(default='http://localhost:8000')

    @computed_field
    @property
    def movies_api_url(self) -> str:
        return urljoin(self.movies_url, '/api/')


settings = Settings()
