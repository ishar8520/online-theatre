from __future__ import annotations

import enum
import uuid

from pydantic import BaseModel


class TemplateType(enum.StrEnum):
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'
    OTHER = 'other'


class Template(BaseModel):
    id: uuid.UUID
    code: str
    subject: str
    body: str
    type: TemplateType
