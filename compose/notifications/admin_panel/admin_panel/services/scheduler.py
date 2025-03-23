from datetime import datetime
import json
from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.triggers.cron import CronTrigger

from admin_panel.schemas.scheduler import SchedulerCreate, SchedulerGet
from admin_panel.db.redis import get_redis_client
from admin_panel.scheduler import scheduler_cron
from uuid import uuid4
from croniter import croniter


def is_valid_cron_expression(cron_expression: str) -> bool:
    try:
        croniter(cron_expression, datetime.now())
        return True
    except ValueError:
        return False

class SchedulerService:
    _redis_client: AsyncSession
    
    def __init__(self, session: AsyncSession):
        self._redis_client = session
        
    async def create(self, scheduler: SchedulerCreate):
        task_id = str(uuid4())
        
        if not is_valid_cron_expression(scheduler.cron_expression):
            raise HTTPException(status_code=400, detail="Некорректное cron-выражение")
        
        trigger = CronTrigger.from_crontab(scheduler.cron_expression)
        scheduler_cron.add_job(self.scheduled_task, trigger, args=[task_id], id=task_id)

        task_data = {
            "task_id": str(task_id),
            "template_id": str(scheduler.template_id),
            "user_id": str(scheduler.user_id),
            "cron_expression": scheduler.cron_expression,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_run": None
        }
        task_data = json.dumps(task_data)
        await self._redis_client.set_value(task_id, task_data)
        return task_id
    
    async def get(self, task_id: str):
        task_data = await self._redis_client.get_value(task_id)
        task_data = json.loads(task_data)
        if not task_data:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        scheduler = SchedulerGet(
            id=UUID(task_id),
            template_id=UUID(task_data["template_id"]),
            user_id=UUID(task_data["user_id"]),
            cron_expression=task_data["cron_expression"],
            created_at=datetime.fromisoformat(task_data["created_at"]),
            updated_at=datetime.fromisoformat(task_data["updated_at"]),
            last_run=task_data["last_run"]
        )
        return scheduler


    async def scheduled_task(self, task_id: str):
        task_data = self._redis_client.get_value(task_id)
        task_data = json.loads(task_data)
        if task_data:
            task_data["last_run"] = datetime.now().isoformat()
            await self._redis_client.set_value(task_id, task_data)

def get_scheduler_service(
    redis_session: AsyncSession = Depends(get_redis_client),
) -> SchedulerService:
    return SchedulerService(redis_session)