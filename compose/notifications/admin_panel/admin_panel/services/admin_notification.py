from datetime import datetime
from functools import lru_cache

from admin_panel.db.postgres import get_postgres_session
from admin_panel.models.admin_notification import AdminNotificationTask
from admin_panel.models.enums import (
    AdminNotificationTaskStatusEnum,
    AdminNotificationTypesEnum,
    DeliveryEnum,
)
from admin_panel.schemas import admin_notification as admin_schemas
from admin_panel.services import exceptions as exc
from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class AdminNotificationService:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def create_admin_notification_task(
        self, notification_data: admin_schemas.CreateAdminNotificationSchema
    ) -> AdminNotificationTask:
        try:
            notification_type = AdminNotificationTypesEnum(notification_data.notification_type)
        except ValueError:
            raise exc.AdminNotificationNotFoundError(
                f"Notification type not found: {notification_data.notification_type}"
            )

        try:
            delivery_type = DeliveryEnum(notification_data.delivery_type)
        except ValueError:
            raise exc.DeliveryNotFoundError(f"Delivery type not found: {notification_data.delivery_type}")

        if notification_data.send_date:
            send_date = notification_data.send_date.replace(tzinfo=None)
        else:
            send_date = datetime.now()

        task = AdminNotificationTask(
            status=AdminNotificationTaskStatusEnum.CREATED,
            notification_type=notification_type,
            delivery_type=delivery_type,
            send_date=send_date,
            template_code=notification_data.template_code,
        )

        async with self.postgres_session as session:
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task

    async def get_admin_notifications_list(self) -> list[AdminNotificationTask]:
        async with self.postgres_session as session:
            notifications_data = await session.scalars(select(AdminNotificationTask))
            return list(notifications_data.all())

    async def update_admin_notification(
        self,
        notification_id: str,
        notification_data: admin_schemas.UpdateNotificationSchema,
    ) -> AdminNotificationTask:
        async with self.postgres_session as session:
            notifications_data = await session.scalars(
                select(AdminNotificationTask).filter_by(id=notification_id)
            )
            notification = notifications_data.first()

            if notification is None:
                raise exc.AdminNotificationNotFoundError("Notification not found")

            for field in notification_data.model_fields_set:
                field_value = getattr(notification_data, field)
                if isinstance(field_value, datetime):
                    field_value = field_value.replace(tzinfo=None)
                setattr(notification, field, field_value)
            try:
                await session.commit()
            except IntegrityError:
                raise exc.DatabaseError("Database integrity error occurred")
            return notification

    async def delete_admin_notification_task(self, notification_id: str):
        async with self.postgres_session as session:
            notifications_data = await session.scalars(
                select(AdminNotificationTask).filter_by(id=notification_id)
            )
            notification = notifications_data.first()

            if notification is None:
                raise exc.AdminNotificationNotFoundError("Notification not found")

            await session.delete(notification)
            await session.commit()


@lru_cache()
def get_admin_notification_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> AdminNotificationService:
    return AdminNotificationService(postgres_session)
