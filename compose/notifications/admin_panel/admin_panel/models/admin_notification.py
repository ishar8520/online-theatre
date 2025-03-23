import uuid
from datetime import datetime
from typing import Optional

from admin_panel.models.enums import (
    AdminNotificationTaskStatusEnum,
    AdminNotificationTypesEnum,
    DeliveryEnum,
    TemplateTypeEnum,
)
from sqlalchemy import Boolean, DateTime, ForeignKey, MetaData, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


admin_metadata_obj = MetaData(
    schema="admin_panel",
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    },
)


class AdminBase(DeclarativeBase):
    """Базовый класс для всех моделей в admin_panel, задающий метаданные и схему."""
    metadata = admin_metadata_obj
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Template(AdminBase):
    __tablename__ = "templates"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    subject: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[TemplateTypeEnum] = mapped_column(
        PG_ENUM(TemplateTypeEnum, name="template_type_enum", create_type=True),
        nullable=False,
    )
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    admin_notifications: Mapped[list["AdminNotificationTask"]] = relationship(
        "AdminNotificationTask", back_populates="template"
    )

    def __repr__(self) -> str:
        return f"<Template id={self.id} subject={self.subject}>"


class AdminNotificationTask(AdminBase):
    __tablename__ = "admin_notifications"

    notification_type: Mapped[AdminNotificationTypesEnum] = mapped_column(
        PG_ENUM(AdminNotificationTypesEnum, name="notification_types_enum", create_type=True),
        nullable=False,
    )
    delivery_type: Mapped[DeliveryEnum] = mapped_column(
        PG_ENUM(DeliveryEnum, name="delivery_enum", create_type=True),
        nullable=False,
    )
    status: Mapped[AdminNotificationTaskStatusEnum] = mapped_column(
        PG_ENUM(AdminNotificationTaskStatusEnum, name="notification_task_status_enum", create_type=True),
        nullable=False,
    )
    send_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    template_code: Mapped[str] = mapped_column(String(100), ForeignKey("templates.code"), nullable=False)

    template: Mapped["Template"] = relationship("Template", back_populates="admin_notifications")

    def __repr__(self) -> str:
        return f"<AdminNotificationTask {self.notification_type} {self.id}>"
