from __future__ import annotations

from pydantic import BaseModel


class ParamsModel(BaseModel):
    def serialize(self) -> dict:
        return {
            key: value
            for key, value in self.model_dump(mode='json').items()
            if value is not None
        }
