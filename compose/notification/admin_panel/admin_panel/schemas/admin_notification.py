from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateAdminNotificationSchema(BaseModel):
    notification_type: str
    delivery_type: str
    send_date: datetime | None = None


class GetAdminNotificationSchema(BaseModel):
    id: UUID
    notification_type: str
    delivery_type: str
    status: str
    created: datetime
    send_date: datetime

    class Config:
        from_attributes = True


class UpdateNotificationSchema(BaseModel):
    send_date: datetime
