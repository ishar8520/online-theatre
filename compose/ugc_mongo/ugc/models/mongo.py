from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

import pymongo
from beanie import Document
from pydantic import Field


class Bookmark(Document):
    user_id: uuid.UUID
    film_id: uuid.UUID
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        collection = "bookmarks"

        indexes = [
            pymongo.IndexModel(
                [
                    ("user_id", pymongo.ASCENDING),
                    ("film_id", pymongo.ASCENDING),
                ],
                unique=True
            )
        ]


class Rate(Document):
    user_id: uuid.UUID
    film_id: uuid.UUID
    rate: int
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        collection = "rates"

        indexes = [
            pymongo.IndexModel(
                [
                    ("user_id", pymongo.ASCENDING),
                    ("film_id", pymongo.ASCENDING),
                ],
                unique=True
            )
        ]


class Review(Document):
    user_id: uuid.UUID
    film_id: uuid.UUID
    text: str
    is_published: bool = False
    published_at: Optional[datetime] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        collection = "reviews"

        indexes = [
            pymongo.IndexModel(
                [
                    ("user_id", pymongo.ASCENDING),
                    ("film_id", pymongo.ASCENDING),
                ],
                unique=True
            )
        ]
