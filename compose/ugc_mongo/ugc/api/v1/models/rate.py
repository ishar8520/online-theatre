from __future__ import annotations

import uuid

from pydantic import BaseModel, field_validator


class RateAdd(BaseModel):
    user_id: uuid.UUID
    film_id: uuid.UUID
    rate: int

    @field_validator('rate')
    def validate_rate(cls, value):
        if value < 1 or value > 10:
            raise ValueError("Rate must be between 1 and 10")
        return value

