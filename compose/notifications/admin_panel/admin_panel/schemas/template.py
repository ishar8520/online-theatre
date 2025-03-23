from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from admin_panel.models.enums import TemplateTypeEnum


class CreateTemplateSchema(BaseModel):
    code: str
    subject: str
    body: str
    type: TemplateTypeEnum


class GetTemplateSchema(BaseModel):
    id: UUID
    code: str
    subject: str
    body: str
    type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UpdateTemplateSchema(BaseModel):
    code: str | None = None
    subject: str | None = None
    body: str | None = None
    type: str | None = None
