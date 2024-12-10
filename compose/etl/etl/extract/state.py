from __future__ import annotations

import datetime
import uuid

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class State(BaseModel):
    model_config = ConfigDict(strict=True)

    last_modified: LastModified = Field(default_factory=lambda: LastModified())


class LastModified(BaseModel):
    model_config = ConfigDict(frozen=True)

    modified: datetime.datetime | None = Field(default=None)
    id: uuid.UUID | None = Field(default=None)
