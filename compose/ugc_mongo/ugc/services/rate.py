from __future__ import annotations

import uuid

from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from .exceptions import (
    NotFoundException,
    DuplicateKeyException
)
from ..models.mongo import Rate


class RateService:
    async def add(
            self,
            user_id: uuid.UUID,
            film_id: uuid.UUID,
            rate: int
    ) -> PydanticObjectId | None:
        try:
            new_rate = Rate(
                user_id=user_id, film_id=film_id, rate=rate
            )
            await new_rate.insert()
        except DuplicateKeyError:
            raise DuplicateKeyException

        return new_rate.id

    async def get_list(self, user_id: uuid.UUID) -> list:
        return await Rate.find(Rate.user_id == user_id).to_list()

    async def delete(
            self,
            id: PydanticObjectId
    ) -> None:
        rate = await Rate.get(id)
        if rate is None:
            raise NotFoundException()

        await rate.delete()
