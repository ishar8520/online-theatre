from __future__ import annotations

from pydantic import BaseModel


class Film(BaseModel):
    id: str
    title: str
    description: str
