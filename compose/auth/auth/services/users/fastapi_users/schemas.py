from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CreateUpdateDictModel(BaseModel):
    def create_update_dict(self):
        return self.model_dump(
            exclude_unset=True,
            exclude={
                "id",
                "is_superuser",
            },
        )

    def create_update_dict_superuser(self):
        return self.model_dump(exclude_unset=True, exclude={"id"})


class UserRead(CreateUpdateDictModel):
    """Base User model."""

    id: uuid.UUID
    login: str
    is_superuser: bool = False

    model_config = ConfigDict(from_attributes=True)  # type: ignore


class UserCreate(CreateUpdateDictModel):
    login: str
    password: str
    is_superuser: Optional[bool] = False


class UserUpdate(CreateUpdateDictModel):
    login: Optional[str] = None
    password: Optional[str] = None
    is_superuser: Optional[bool] = None
