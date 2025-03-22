from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from admin_panel.schemas import admin_notification as admin_schemas
from admin_panel.services import admin_notification as admin_services
from admin_panel.services.exceptions import AdminNotificationNotFoundError, DeliveryNotFoundError
from fastapi_pagination import Page, paginate

router = APIRouter()


@router.post(
    "/",
    response_model=dict,
    summary="Создать задачу на рассылку",
)
async def send_notifications(
    notification_data: admin_schemas.CreateAdminNotificationSchema,
    notification_service: admin_services.AdminNotificationService = Depends(
        admin_services.get_admin_notification_service
    ),
):
    try:
        await notification_service.create_admin_notification_task(notification_data=notification_data)
        return {"detail": "success"}
    except AdminNotificationNotFoundError as notification_type_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(notification_type_error),
        )
    except DeliveryNotFoundError as delivery_type_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(delivery_type_error),
        )
    except ValidationError as validation_error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(validation_error),
        )


@router.get(
    "/",
    response_model=Page[admin_schemas.GetAdminNotificationSchema],
    summary="Получить задачи на рассылку",
)
async def get_notifications(
    notification_service: admin_services.AdminNotificationService = Depends(
        admin_services.get_admin_notification_service
    ),
) -> Page[admin_schemas.GetAdminNotificationSchema]:
    notifications_list = await notification_service.get_admin_notifications_list()
    return paginate(notifications_list)


@router.patch(
    "/{notification_id}",
    response_model=admin_schemas.GetAdminNotificationSchema,
    summary="Обновить задачу на рассылку нотификаций",
)
async def update_notification(
    notification_id: str,
    notification_data: admin_schemas.UpdateNotificationSchema,
    notification_service: admin_services.AdminNotificationService = Depends(
        admin_services.get_admin_notification_service
    ),
):
    try:
        return await notification_service.update_admin_notification(
            notification_id=notification_id, notification_data=notification_data
        )
    except AdminNotificationNotFoundError as notification_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(notification_error)
        )


@router.delete(
    "/{notification_id}",
    response_model=dict,
    summary="Удалить задачу на рассылку нотификаций",
    description="Удаление задачи на отправку сообщений",
)
async def delete_notification(
    notification_id: str,
    notification_service: admin_services.AdminNotificationService = Depends(
        admin_services.get_admin_notification_service
    ),
):
    try:
        await notification_service.delete_admin_notification_task(
            notification_id=notification_id
        )
        return {"detail": "success"}
    except AdminNotificationNotFoundError as notification_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(notification_error)
        )

