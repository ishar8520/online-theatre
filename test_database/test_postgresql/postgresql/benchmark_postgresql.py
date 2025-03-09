import psycopg2
import logging
import random

from generator.data_generator import GenerateData
from generator.data_connector import PostgresConnector
from generator.constants import DSL, TOTAL_GENERATE_DATA
from helpers import measure_time, output_result


logging.basicConfig(level=logging.DEBUG)


def load_data(pg_reader):
    """
    Генерация данных для базы данных в таблицах likes, reviews, bokkmarks
    """
    data_generator = GenerateData(TOTAL_GENERATE_DATA)
    data_types = ('likes', 'reviews', 'bookmarks')
    try:
        for data in data_types:
            logging.debug(f'Generate data: {data}, TOTAL_GENRATE_DATA: {TOTAL_GENERATE_DATA}')
            b = 0
            for batch in data_generator.generate_data(data):
                b += len(batch)
                logging.debug(f'Insert data {b}/{TOTAL_GENERATE_DATA}')
                pg_reader.insert_data(batch, table_name=data)
    except Exception as err:
        pg_reader.close_cursor()
        logging.debug(f'Error while inserting data!')


class DataProcessor:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    @measure_time('Чтение списка лайков')
    def read_data_likes(self):
        """Чтение списка лайков и измерение времени исполнения запроса."""
        query = 'SELECT * FROM likes WHERE rating=0;'
        likes_rows = self.db_manager.fetch_data(query)
        logging.info(f'Лайки: {len(likes_rows)}')

    @measure_time('Чтение списка дизлайков')
    def read_data_dislikes(self):
        """Чтение списка дизлайков и измерение времени исполнения запроса."""
        query = 'SELECT * FROM likes WHERE rating=10;'
        dislikes_rows = self.db_manager.fetch_data(query)
        logging.info(f'Дизлайки: {len(dislikes_rows)}')

    @measure_time('Чтение списка лайков и дизлайков у определенного фильма')
    def read_data_film_likes(self, select_film):
        """Чтение списка лайков и дизлайков у определенного фильма."""
        query = f"SELECT * FROM likes where movie_id='{select_film}'"
        rows = self.db_manager.fetch_data(query)
        likes = [row for row in rows if row[3] == 0]
        dislikes = [row for row in rows if row[3] == 10]

        logging.info(f'Дизлайки фильма "{select_film}": {len(dislikes)}')
        logging.info(f'Лайки фильма "{select_film}": {len(likes)}')

    @measure_time('Чтение списка ревью у определенного фильма')
    def read_data_film_reviews(self, select_film):
        """Чтение списка ревью у определенного фильма."""
        query = f"SELECT * FROM reviews where movie_id='{select_film}'"
        rows = self.db_manager.fetch_data(query)
        logging.info(f'Количество ревью фильма "{select_film}": {len(rows)}')

    @measure_time('Чтение средней оценки определенного фильма')
    def read_data_film_avg_rating(self, select_film):
        """Чтение средней оценки фильма."""
        query = f"SELECT * FROM likes where movie_id='{select_film}'"
        rows = self.db_manager.fetch_data(query)
        rating = [row[3] for row in rows]

        avg_rating = round(sum(rating) / len(rating), 2)
        logging.info(f'Средняя оценка фильма "{select_film}": {avg_rating}')

    @measure_time('Чтение списка закладок определенного фильма')
    def read_data_film_bookmarks(self, select_film):
        """Чтение списка закладок фильма."""
        query = f"SELECT * FROM bookmarks where movie_id='{select_film}'"
        rows = self.db_manager.fetch_data(query)
        logging.info(f'Количество закладок фильма "{select_film}": {len(rows)}')
        
    def get_film(self, table):
        """Получить случайное название фильма из БД"""
        query = f'SELECT * FROM {table};'
        rows = self.db_manager.fetch_data(query)
        return random.choice(rows)[2]

if __name__ == '__main__':
    logging.debug(f'Подключение к базе данных: {DSL}')
    with psycopg2.connect(**DSL) as connection:
        pg_reader = PostgresConnector(connection)
        data_process = DataProcessor(pg_reader)
        load_data(pg_reader)
        data_process.read_data_likes()
        data_process.read_data_dislikes()
        data_process.read_data_film_likes(data_process.get_film('likes'))
        data_process.read_data_film_reviews(data_process.get_film('reviews'))
        data_process.read_data_film_avg_rating(data_process.get_film('likes'))
        data_process.read_data_film_bookmarks(data_process.get_film('bookmarks'))
        for result in output_result():
            logging.info(result)
