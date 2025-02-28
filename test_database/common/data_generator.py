import random
from datetime import datetime, timedelta
from typing import Iterator, Union
from uuid import UUID, uuid4

from constants import (BATCH_SIZE, MAX_REVIEW_LEN, QUANTITY_MOVIES,
                       QUANTITY_USERS)
from data_models import Bookmark, Like, Review

from faker import Faker

fake = Faker()


class GenerateData:
    def __init__(self, records_num: int):
        self.records_num = records_num

    @staticmethod
    def __generate_base_movies(quantity: int = QUANTITY_MOVIES) -> list[str]:
        return [fake.catch_phrase() for _ in range(quantity)]

    @staticmethod
    def __generate_base_users(quantity: int = QUANTITY_USERS) -> list[UUID]:
        return [uuid4() for _ in range(quantity)]

    def generate_data(self, data_type: str) -> Iterator[list[Union[Like, Review, Bookmark]]]:
        seen = set()
        # movie_id = random.choice(self.__generate_base_movies())
        # user_id = random.choice(self.__generate_base_movies())
        # print(self.__generate_base_users())
        for _ in range(0, self.records_num, BATCH_SIZE):
            batch = []
            for _ in range(BATCH_SIZE):
                movie_id = random.choice(self.__generate_base_movies())
                user_id = random.choice(self.__generate_base_users())
                if (user_id, movie_id) not in seen:
                    if data_type == "like":
                        record = self._generate_like(user_id, movie_id)
                    elif data_type == "review":
                        record = self._generate_review(user_id, movie_id)
                    elif data_type == "bookmark":
                        record = self._generate_bookmark(user_id, movie_id)
                    else:
                        raise ValueError("Invalid data_type. Use 'like', 'review' or 'bookmark'.")
                    batch.append(record)
                    seen.add((user_id, movie_id))
            print()
            yield batch

    @staticmethod
    def _generate_like(user_id: UUID, movie_id: str) -> Like:
        return Like(
            user_id=user_id,
            movie_id=movie_id,
            rating=random.choice([0, 10]),
            timestamp=datetime.now() - timedelta(days=random.randint(0, 365)),
        )

    @staticmethod
    def _generate_review(user_id: UUID, movie_id: str) -> Review:
        return Review(
            user_id=user_id,
            movie_id=movie_id,
            rating=random.choice([0, 10]),
            text=fake.text(max_nb_chars=MAX_REVIEW_LEN),
            review_likes=random.randint(0, 10),
            timestamp=datetime.now() - timedelta(days=random.randint(0, 365)),
        )

    @staticmethod
    def _generate_bookmark(user_id: UUID, movie_id: str) -> Bookmark:
        return Bookmark(
            user_id=user_id,
            movie_id=movie_id,
            timestamp=datetime.now() - timedelta(days=random.randint(0, 365)),
        )
