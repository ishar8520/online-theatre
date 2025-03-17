import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, ENUM as PG_ENUM
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from notification_api.models.enums import AdminNotificationTypesEnum, DeliveryEnum, AdminNotificationTaskStatusEnum


class Base(DeclarativeBase):
    pass


# Пример таблицы с шаблонами, лучше вынести в отдельный файл
class Template(Base):
    __tablename__ = "templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    # Обратная связь для уведомлений
    admin_notifications: Mapped[list["AdminNotificationTask"]] = relationship(
        "AdminNotificationTask", back_populates="template"
    )


class AdminNotificationTask(Base):
    __tablename__ = "admin_notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
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
    created: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    send_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("templates.id"),
        nullable=False,
    )

    # Связь с таблицей шаблонов
    template: Mapped["Template"] = relationship("Template", back_populates="admin_notifications")

    def __repr__(self) -> str:
        return f"<AdminNotificationTask {self.notification_type} {self.id}>"
