from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class SchedulerCreate(BaseModel):
    notification_type: str
    delivery_type: str
    template_code: str
    send_date: datetime | None = None
    cron_expression: str

class SchedulerGet(BaseModel):
    id: UUID
    notification_type: str
    delivery_type: str
    template_code: str
    send_date: datetime | None = None
    cron_expression: str
    created_at: datetime
    updated_at: datetime
    last_run: str | None

    class Config:
        from_attributes = True

class SchedulerUpdate(BaseModel):
    notification_type: str | None = None,
    delivery_type: str | None = None,
    template_code: str | None = None,
    send_date: datetime | None = None,
    cron_expression: str | None = None,
    last_run: str | None = None,