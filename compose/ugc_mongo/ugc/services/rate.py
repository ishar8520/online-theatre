from __future__ import annotations

import uuid

from .exceptions import NotFoundException
from ..models.mongo import Rate


class RateService:
    async def add(
            self,
            user_id: uuid.UUID,
            film_id: uuid.UUID,
            rate: int
    ) -> uuid.UUID:
        new_rate = Rate(
            user_id=user_id, film_id=film_id, rate=rate
        )
        await new_rate.insert()
        return new_rate.id

    async def get_list(self, user_id: uuid.UUID) -> list:
        return await Rate.find(Rate.user_id == user_id).to_list()

    async def delete(
            self,
            uuid: uuid.UUID
    ) -> None:
        rate = await Rate.get(uuid)
        if rate is None:
            raise NotFoundException()

        await rate.delete()
