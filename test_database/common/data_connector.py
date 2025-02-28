from abc import ABC, abstractmethod
from typing import Union

from data_models import Bookmark, Like, Review
from psycopg2 import extensions, sql


class DataBaseConnector(ABC):
    @abstractmethod
    def insert_data(self, data: list[Union[Like, Review, Bookmark]]) -> None: ...


class PostgresConnector(DataBaseConnector):
    def __init__(self, conn: extensions.connection):
        self.conn = conn
        self.cursor = conn.cursor()

    def close_cursor(self):
        if self.cursor:
            self.cursor.close()

    def insert_data(self, data: list[Union[Like, Review, Bookmark]], table_name: str) -> None:
        data_to_dict = [item.model_dump() for item in data]
        columns = data_to_dict[0].keys()
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.Placeholder() * len(columns)),
        )
        data_db = [tuple(item.values()) for item in data_to_dict]
        try:
            self.cursor.executemany(query, data_db)
            self.conn.commit()
        except Exception as er:
            self.conn.rollback()
            raise

class MongodbConnector(DataBaseConnector):
    def __init__(self):
        ...
    
    def insert_data(self, data):
        ...
