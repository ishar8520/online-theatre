from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from admin_panel.models.enums import TemplateTypeEnum


class SchedulerCreate(BaseModel):
    template_id: UUID
    user_id: UUID
    cron_expression: str

class SchedulerGet(BaseModel):
    id: UUID
    template_id: UUID
    user_id: UUID
    cron_expression: str
    created_at: datetime
    updated_at: datetime
    last_run: str | None

    class Config:
        from_attributes = True


# class UpdateScheduler(BaseModel):
#     code: str | None = None
#     subject: str | None = None
#     body: str | None = None
#     type: str | None = None
