import random
from datetime import datetime, timedelta
from typing import Iterator, Union
from uuid import UUID, uuid4

from faker import Faker

from .constants import BATCH_SIZE, MAX_REVIEW_LEN, QUANTITY_MOVIES, QUANTITY_USERS
from .data_models import Bookmark, Like, Review

fake = Faker()


class GenerateData:
    def __init__(self, records_num: int):
        self.records_num = records_num

    @staticmethod
    def __generate_base_movies(quantity: int = QUANTITY_MOVIES) -> list[str]:
        return [fake.sentence(nb_words=3) for _ in range(quantity)]

    @staticmethod
    def __generate_base_users(quantity: int = QUANTITY_USERS) -> list[UUID]:
        return [str(uuid4()) for _ in range(quantity)]

    def generate_data(self, data_type: str) -> Iterator[list[Union[Like, Review, Bookmark]]]:
        seen = set()
        for _ in range(0, self.records_num, BATCH_SIZE):
            batch = []
            movie_titles = self.__generate_base_movies()
            user_ids = self.__generate_base_users()

            for _ in range(BATCH_SIZE):
                user_id = random.choice(user_ids)
                movie_title = random.choice(movie_titles)
                if data_type == "likes":
                    record = self._generate_like(user_id, movie_title)
                elif data_type == "reviews":
                    record = self._generate_review(user_id, movie_title)
                elif data_type == "bookmarks":
                    record = self._generate_bookmark(user_id, movie_title)
                else:
                    raise ValueError("Invalid data_type. Use 'likes', 'reviews' or 'bookmarks'.")
                batch.append(record)
                seen.add((user_id, movie_title))
            yield batch

    @staticmethod
    def _generate_like(user_id: UUID, movie_id: str) -> Like:
        return Like(
            user_id=str(user_id),
            movie_id=movie_id,
            rating=random.choice([0, 10]),
            created_at=datetime.now() - timedelta(days=random.randint(0, 365)),
        )

    @staticmethod
    def _generate_review(user_id: UUID, movie_id: str) -> Review:
        return Review(
            user_id=str(user_id),
            movie_id=movie_id,
            rating=random.choice([0, 10]),
            text=fake.text(max_nb_chars=MAX_REVIEW_LEN),
            review_likes=random.randint(0, 10),
            created_at=datetime.now() - timedelta(days=random.randint(0, 365)),
        )

    @staticmethod
    def _generate_bookmark(user_id: UUID, movie_id: str) -> Bookmark:
        return Bookmark(
            user_id=str(user_id),
            movie_id=movie_id,
            created_at=datetime.now() - timedelta(days=random.randint(0, 365)),
        )
