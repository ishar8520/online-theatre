from __future__ import annotations

import uuid

from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from .exceptions import NotFoundException, DuplicateKeyException
from ..models.mongo import Bookmark


class BookmarkService:
    async def add(
            self,
            user_id: uuid.UUID,
            film_id: uuid.UUID
    ) -> PydanticObjectId | None:
        try:
            new_bookmark = Bookmark(
                user_id=user_id, film_id=film_id
            )
            await new_bookmark.insert()
        except DuplicateKeyError:
            raise DuplicateKeyException

        return new_bookmark.id

    async def get_list(
            self,
            user_id: uuid.UUID
    ) -> list:
        return await Bookmark.find(Bookmark.user_id == user_id).to_list()

    async def delete(self, id: PydanticObjectId) -> None:
        bookmark = await Bookmark.get(id)
        if bookmark is None:
            raise NotFoundException()

        await bookmark.delete()
