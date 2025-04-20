from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class PaymentSchema(BaseModel):
    id: UUID
    user_id: UUID
    ps_name: str | None = None
    ps_invoice_id: UUID | None = None
    status: str
    created_at: datetime
    modified_at: datetime

    class Config:
        from_attributes = True
