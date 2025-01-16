from __future__ import annotations

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr

from .models import ID

SCHEMA = TypeVar("SCHEMA", bound=BaseModel)


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


class BaseUser(CreateUpdateDictModel, Generic[ID]):
    """Base User model."""

    id: ID
    email: EmailStr
    is_superuser: bool = False

    model_config = ConfigDict(from_attributes=True)  # type: ignore


class BaseUserCreate(CreateUpdateDictModel):
    email: EmailStr
    password: str
    is_superuser: Optional[bool] = False


class BaseUserUpdate(CreateUpdateDictModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    is_superuser: Optional[bool] = None


U = TypeVar("U", bound=BaseUser)
UC = TypeVar("UC", bound=BaseUserCreate)
UU = TypeVar("UU", bound=BaseUserUpdate)
