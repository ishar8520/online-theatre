from __future__ import annotations

import logging

from ..broker import broker
from ..services.auth import User

logger = logging.getLogger(__name__)


@broker.task
async def send_notification_task(*, user: User) -> None:
    logger.info(user)
