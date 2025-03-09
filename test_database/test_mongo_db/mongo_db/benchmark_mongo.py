import logging
import random

from generator.constants import MONGO_DSL, MONGO_NAME, TOTAL_GENERATE_DATA
from generator.data_connector import MongoConnector
from generator.data_generator import GenerateData
from helpers import measure_time, output_result
from pymongo import MongoClient

logging.basicConfig(level=logging.DEBUG)

def load_data(mongo_connector: MongoConnector) -> None:
    """
    Генерация данных для базы данных в коллекциях likes, reviews, bookmarks
    """
    data_generator = GenerateData(TOTAL_GENERATE_DATA)
    data_types = ("likes", "reviews", "bookmarks")
    for data in data_types:
        logging.debug(f"Generate data: {data}, TOTAL_GENERATE_DATA: {TOTAL_GENERATE_DATA}")
        b = 0
        for batch in data_generator.generate_data(data):
            b += len(batch)
            logging.debug(f"Insert data {b}/{TOTAL_GENERATE_DATA}")
            mongo_connector.insert_data(batch, table_name=data)


class DataProcessor:
    def __init__(self, mongo_connector: MongoConnector):
        self.mongo_connector = mongo_connector

    @measure_time("Чтение списка лайков")
    def read_data_likes(self) -> None:
        """Чтение списка лайков и измерение времени исполнения запроса."""
        likes = self.mongo_connector.fetch_data({"rating": 0}, "likes")
        logging.info(f"Лайки: {len(likes)}")

    @measure_time("Чтение списка дизлайков")
    def read_data_dislikes(self) -> None:
        """Чтение списка дизлайков и измерение времени исполнения запроса."""
        dislikes = self.mongo_connector.fetch_data({"rating": 10}, "bookmarks")
        logging.info(f"Дизлайки: {len(dislikes)}")

    @measure_time("Чтение списка лайков и дизлайков у определенного фильма")
    def read_data_film_likes(self, select_film: str) -> None:
        """Чтение списка лайков и дизлайков у определенного фильма."""
        likes = self.mongo_connector.fetch_data({"movie_id": select_film, "rating": 0}, "likes")
        dislikes = self.mongo_connector.fetch_data({"movie_id": select_film, "rating": 10}, "likes")
        logging.info(f'Дизлайки фильма "{select_film}": {len(dislikes)}')
        logging.info(f'Лайки фильма "{select_film}": {len(likes)}')

    @measure_time("Чтение списка ревью у определенного фильма")
    def read_data_film_reviews(self, select_film: str) -> None:
        """Чтение списка ревью у определенного фильма."""
        reviews = self.mongo_connector.fetch_data({"movie_id": select_film}, "reviews")
        logging.info(f'Количество ревью фильма "{select_film}": {len(reviews)}')

    @measure_time("Чтение средней оценки определенного фильма")
    def read_data_film_avg_rating(self, select_film: str) -> None:
        """Чтение средней оценки фильма."""
        ratings = [doc["rating"] for doc in self.mongo_connector.fetch_data({"movie_id": select_film}, "likes")]
        avg_rating = round(sum(ratings) / len(ratings), 2)
        logging.info(f'Средняя оценка фильма "{select_film}": {avg_rating}')

    @measure_time("Чтение списка закладок определенного фильма")
    def read_data_film_bookmarks(self, select_film: str) -> None:
        """Чтение списка закладок фильма."""
        bookmarks = self.mongo_connector.fetch_data({"movie_id": select_film}, "bookmarks")
        logging.info(f'Количество закладок фильма "{select_film}": {len(bookmarks)}')

    def get_film(self, collection_name: str) -> str: #mongo_connector: MongoConnector, ) -> str:
        """Получить случайное название фильма из коллекции"""
        films = self.mongo_connector.fetch_data({}, collection_name)
        return random.choice(films)["movie_id"]

if __name__ == "__main__":
    logging.debug(f"Подключение к базе данных: {MONGO_DSL}")
    client = MongoClient(**MONGO_DSL)
    db_name = MONGO_NAME

    mongo_connector = MongoConnector(client, db_name)
    data_process = DataProcessor(mongo_connector)

    load_data(mongo_connector)
    data_process.read_data_likes()
    data_process.read_data_dislikes()
    data_process.read_data_film_likes(data_process.get_film("likes"))
    data_process.read_data_film_reviews(data_process.get_film("reviews"))
    data_process.read_data_film_avg_rating(data_process.get_film("likes"))
    data_process.read_data_film_bookmarks(data_process.get_film("bookmarks"))
    for result in output_result():
        logging.info(result)
