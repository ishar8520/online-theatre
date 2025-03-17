from datetime import datetime
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_postgres_session
from models.enums import DeliveryEnum, AdminNotificationTypesEnum, AdminNotificationTaskStatusEnum

from models.admin_notification import AdminNotificationTask
from schemas import admin_notification as admin_schemas
from services import exceptions as exc


class AdminNotificationService:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def create_admin_notification_task(
        self, notification_data: admin_schemas.CreateAdminNotificationSchema
    ) -> AdminNotificationTask:
        try:
            notification_type = NotificationTypesEnum(notification_data.notification_type)
        except ValueError:
            raise exc.NotificationNotFoundError("Notification type not found")

        try:
            delivery_type = DeliveryEnum(notification_data.delivery_type)
        except ValueError:
            raise exc.ChannelNotFoundError("Channel not found")

        if notification_data.send_date:
            send_date = notification_data.send_date.replace(tzinfo=None)
        else:
            send_date = func.now()

        task = AdminNotificationTask(
            status=AdminNotificationTaskStatusEnum.CREATED,
            notification_type=notification_type,
            delivery_type=delivery_type,
            send_date=send_date,
            template_id=notification_data.template_id,
        )

        async with self.postgres_session() as session:
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task

    async def get_admin_notifications_list(self) -> list[AdminNotificationTask]:
        async with self.postgres_session() as session:
            notifications_data = await session.scalars(select(AdminNotificationTask))
            return notifications_data.all()

    async def update_admin_notification(
        self,
        notification_id: str,
        notification_data: admin_schemas.UpdateNotificationSchema,
    ) -> AdminNotificationTask:
        async with self.postgres_session() as session:
            notifications_data = await session.scalars(
                select(AdminNotificationTask).filter_by(id=notification_id)
            )
            notification = notifications_data.first()

            if notification is None:
                raise exc.NotificationNotFoundError("Notification not found")

            for field in notification_data.model_fields_set:
                field_value = getattr(notification_data, field)
                if isinstance(field_value, datetime):
                    field_value = field_value.replace(tzinfo=None)
                setattr(notification, field, field_value)
            try:
                await session.commit()
            except IntegrityError:
                raise exc.ConflictError("ConflictError")
            return notification

    async def delete_admin_notification_task(self, notification_id: str):
        async with self.postgres_session() as session:
            notifications_data = await session.scalars(
                select(AdminNotificationTask).filter_by(id=notification_id)
            )
            notification = notifications_data.first()

            if notification is None:
                raise exc.NotificationNotFoundError("Notification not found")

            await session.delete(notification)
            await session.commit()


@lru_cache()
def get_admin_notification_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> AdminNotificationService:
    return AdminNotificationService(postgres_session)
