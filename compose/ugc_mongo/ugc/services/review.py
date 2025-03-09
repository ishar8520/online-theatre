from __future__ import annotations

import uuid
from datetime import datetime, timezone

from beanie import PydanticObjectId

from .exceptions import NotFoundException
from ..models.mongo import Review


class ReviewService:
    async def add(
            self,
            user_id: uuid.UUID,
            film_id: uuid.UUID,
            text: str,
            is_published: bool
    ) -> PydanticObjectId | None:
        new_review = Review(
            user_id=user_id,
            film_id=film_id,
            text=text,
            is_published=is_published
        )
        if is_published:
            new_review.published_at = datetime.now(timezone.utc)

        await new_review.insert()
        return new_review.id

    async def get_list(self, user_id: uuid.UUID) -> list:
        return await Review.find(Review.user_id == user_id).to_list()

    async def publish(self, id: PydanticObjectId) -> PydanticObjectId:
        review = await Review.get(id)
        if review is None:
            raise NotFoundException()

        review.is_published = True
        review.published_at = datetime.now(timezone.utc)
        await review.save()

        return id

    async def update(self, id: PydanticObjectId, text: str) -> PydanticObjectId:
        review = await Review.get(id)
        if review is None:
            raise NotFoundException()

        review.text = text
        await review.save()

        return id

    async def delete(
            self,
            id: PydanticObjectId
    ) -> None:
        review = await Review.get(id)
        if review is None:
            raise NotFoundException()

        await review.delete()
