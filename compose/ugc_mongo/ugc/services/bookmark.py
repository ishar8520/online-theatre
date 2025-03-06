from __future__ import annotations

import uuid

from .exceptions import NotFoundException
from ..models.mongo import Bookmark


class BookmarkService:
    async def add(self, user_id: uuid.UUID, film_id: uuid.UUID) -> uuid.UUID:
        new_bookmark = Bookmark(
            user_id=user_id, film_id=film_id
        )
        await new_bookmark.insert()
        return new_bookmark.id

    async def get_list(self) -> list:
        return await Bookmark.find().to_list()

    async def delete(self, uuid: uuid.UUID) -> None:
        bookmark = await Bookmark.get(uuid)
        if bookmark is None:
            raise NotFoundException()

        await bookmark.delete()
