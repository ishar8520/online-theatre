from datetime import datetime
import json
from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.triggers.cron import CronTrigger

from admin_panel.schemas.scheduler import SchedulerCreate, SchedulerGet, SchedulerUpdate
from admin_panel.db.redis import get_redis_client, RedisClient
from admin_panel.scheduler import scheduler_cron
from admin_panel.core.config import settings
from uuid import uuid4
from croniter import croniter
import httpx
import logging

logging.basicConfig(level=logging.INFO)


def is_valid_cron_expression(cron_expression: str) -> bool:
    try:
        croniter(cron_expression, datetime.now())
        return True
    except ValueError:
        return False


class SchedulerService:
    _redis_client: RedisClient
    _http_client: httpx.AsyncClient
    
    def __init__(self, session: RedisClient):
        self._redis_client = session
        self._http_client = httpx.AsyncClient()

    async def create(self, scheduler: SchedulerCreate):
        task_id = str(uuid4())
        
        if not is_valid_cron_expression(scheduler.cron_expression):
            raise HTTPException(status_code=400, detail="Некорректное cron-выражение")
        
        trigger = CronTrigger.from_crontab(scheduler.cron_expression)
        scheduler_cron.add_job(self.scheduled_task, trigger, args=[task_id], id=task_id)

        task_data = {
            "task_id": str(task_id),
            "notification_type": str(scheduler.notification_type),
            "delivery_type": str(scheduler.delivery_type),
            "template_code": scheduler.template_code,
            "send_date": scheduler.send_date.isoformat() if scheduler.send_date else None,
            "cron_expression": scheduler.cron_expression,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_run": None
        }
        await self._redis_client.set_value(task_id, json.dumps(task_data))
        return task_id
    
    async def get(self, task_id: str):
        task_data = await self._redis_client.get_value(task_id)
        if not task_data:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        task_data = json.loads(task_data)
        scheduler = SchedulerGet(
            id=UUID(task_id),
            notification_type=task_data["notification_type"],
            delivery_type=task_data["delivery_type"],
            template_code=task_data["template_code"],
            send_date=task_data["send_date"],
            cron_expression=task_data["cron_expression"],
            created_at=datetime.fromisoformat(task_data["created_at"]),
            updated_at=datetime.fromisoformat(task_data["updated_at"]),
            last_run=task_data["last_run"]
        )
        return scheduler

    async def update(self, task_id: str, scheduler: SchedulerUpdate) -> SchedulerGet:
        task_data = await self._redis_client.get_value(task_id)
        task_data = json.loads(task_data)
        if not task_data:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        if scheduler.cron_expression:
            if not is_valid_cron_expression(scheduler.cron_expression):
                raise HTTPException(status_code=400, detail="Некорректное cron-выражение")   
        
        updated = datetime.now()
        task_data.update({
            "notification_type": (
                str(scheduler.notification_type)
                if scheduler.notification_type
                else task_data["notification_type"]
            ),
            "delivery_type": (
                str(scheduler.delivery_type)
                if scheduler.delivery_type
                else task_data["delivery_type"]
            ),
            "template_code": (
                scheduler.template_code
                if scheduler.template_code
                else task_data["template_code"]
            ),
            "send_date": (
                scheduler.send_date.isoformat()
                if scheduler.send_date
                else None
                if scheduler.send_date is None
                else task_data["send_date"]
            ),
            "cron_expression": (
                scheduler.cron_expression
                if scheduler.cron_expression
                else task_data["cron_expression"]
            ),
            "updated_at": updated,
            "last_run": (
                scheduler.last_run
                if scheduler.last_run
                else task_data["last_run"]
            )
        })
        
        await self._redis_client.set_value(task_id, json.dumps(task_data))

        updated_scheduler = SchedulerGet(
            id=UUID(task_id),
            notification_type=task_data["notification_type"],
            delivery_type=task_data["delivery_type"],
            template_code=task_data["template_code"],
            send_date=task_data["send_date"],
            cron_expression=task_data["cron_expression"],
            created_at=datetime.fromisoformat(task_data["created_at"]),
            updated_at=updated,
            last_run=task_data["last_run"]
        )

        return updated_scheduler

    async def delete(self, task_id: str):
        job = scheduler_cron.get_job(task_id)
        if not job:
            logging.warning(f"Задача с task_id {task_id} не найдена в планировщике")
            raise HTTPException(status_code=404, detail="Задача не найдена в планировщике")
        
        scheduler_cron.remove_job(task_id)
        task_data = await self._redis_client.get_value(task_id)
        if not task_data:
            raise HTTPException(status_code=404, detail="Задача не найдена") 
        return await self._redis_client.delete_value(task_id)
    
    async def scheduled_task(self, task_id: str):
        task_data = await self._redis_client.get_value(task_id)
        if not task_data:
            return

        task_data = json.loads(task_data)
        notification_data = {
            "notification_type": task_data["notification_type"],
            "delivery_type": task_data["delivery_type"],
            "template_code": task_data["template_code"],
            "send_date": task_data["send_date"],
        }
        try:
            response = await self._http_client.post(
                f"http://{settings.admin_notification.host}:{settings.admin_notification.port}/admin_panel/api/v1/admin_notification/",
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                json=notification_data
            )
            logging.info(f"Ответ от API: {response.status_code}, {response.text}")
            response.raise_for_status()
            logging.info(f"Задача {task_id} из планировщика успешно отправлена")
        except httpx.HTTPError as e:
            logging.warning(f"Ошибка при выполнении запроса: {e}")
        finally:
            task_data["last_run"] = datetime.now().isoformat()
            await self._redis_client.set_value(task_id, json.dumps(task_data))


def get_scheduler_service(
    redis_session: RedisClient = Depends(get_redis_client),
) -> SchedulerService:
    return SchedulerService(redis_session)
