from fastapi import APIRouter, Depends

from admin_panel.schemas import scheduler as scheduler_schemas
from admin_panel.services import scheduler as scheduler_services

router = APIRouter()


@router.post(
    "/",
    response_model=dict,
    summary="Создать отложенную задачу на рассылку",
)
async def create_scheduler(
    scheduler: scheduler_schemas.SchedulerCreate,
    scheduler_service: scheduler_services.SchedulerService = Depends(scheduler_services.get_scheduler_service)
):
    task_id = await scheduler_service.create(scheduler)
    return {'detail': 'success',
            'task_id': task_id}


@router.get(
    "/{task_id}",
    response_model=scheduler_schemas.SchedulerGet,
    summary='Получить задачу по id'
)
async def get_scheduler(
    task_id=str,
    scheduler_service: scheduler_services.SchedulerService = Depends(scheduler_services.get_scheduler_service)
):
    response = await scheduler_service.get(task_id)
    return response


@router.patch(
    "/{task_id}",
    response_model=scheduler_schemas.SchedulerGet,
    summary='Обновить задачу по id'
)
async def update_scheduler(
    task_id: str,
    scheduler: scheduler_schemas.SchedulerUpdate,
    scheduler_service: scheduler_services.SchedulerService = Depends(scheduler_services.get_scheduler_service)
):
    response = await scheduler_service.update(task_id, scheduler)
    return response


@router.delete(
    "/{task_id}",
    response_model=dict,
    summary='Удалить задачу по id'
)
async def delete_scheduler(
    task_id: str,
    scheduler_service: scheduler_services.SchedulerService = Depends(scheduler_services.get_scheduler_service)
):
    await scheduler_service.delete(task_id)
    return {
        'detail': 'success',
        'task_id': task_id,
    }
