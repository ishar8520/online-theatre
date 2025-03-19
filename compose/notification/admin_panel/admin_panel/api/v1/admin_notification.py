from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from admin_panel.schemas import admin_notification as admin_schemas
from admin_panel.services import admin_notification as admin_services
from admin_panel.services.exceptions import AdminNotificationNotFoundError, DeliveryNotFoundError

router = APIRouter()


@router.post(
    "/",
    response_model=dict,
    description="Создать задачу на рассылку",
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
