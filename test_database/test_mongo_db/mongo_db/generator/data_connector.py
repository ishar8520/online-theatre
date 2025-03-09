from abc import ABC, abstractmethod
from typing import Union

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from .data_models import Bookmark, Like, Review


class DataBaseConnector(ABC):
    @abstractmethod
    def insert_data(self, data: list[Union[Like, Review, Bookmark]]) -> None: ...


class MongoConnector(DataBaseConnector):
    """Класс подключения к MongoDB"""

    def __init__(self, conn: MongoClient, db_name: str):
        self.conn = conn
        self.db: Database = conn[db_name]
        self.collection: Collection = None

    def insert_data(self, data: list[Union[Like, Review, Bookmark]], table_name: str) -> None:
        """Вставка данных в коллекцию MongoDB"""
        data_to_dict = [item.model_dump() for item in data]
        self.collection = self.db[table_name]
        try:
            self.collection.insert_many(data_to_dict)
        except Exception as err:
            raise Exception(f"Ошибка при вставке данных в MongoDB: {err}")

    def fetch_data(self, query: dict, table_name: str):
        """Чтение данных из коллекции MongoDB"""
        # if not self.collection:
        #     raise Exception("Коллекция не выбрана")
        collection = self.db[table_name]
        return list(collection.find(query))
