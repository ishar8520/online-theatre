import psycopg2
import logging
import random

from generator.data_generator import GenerateData
from generator.data_connector import PostgresConnector
from generator.constants import DSL, TOTAL_GENERATE_DATA
from helpers import measure_time, output_result


logging.basicConfig(level=logging.DEBUG)


def get_film(connection, table):
    """Получить случайное название фильма из БД"""
    pg_reader = PostgresConnector(connection)
    try:
        query = f'SELECT * FROM {table};'
        rows = pg_reader.fetch_data(query)
        return random.choice(rows)[2]
    finally:
        pg_reader.close_cursor()


def load_data(connection):
    """
    Генерация данных для базы данных в таблицах likes, reviews, bokkmarks
    """
    pg_loader = PostgresConnector(connection)
    data_generator = GenerateData(TOTAL_GENERATE_DATA)
    data_types = ('likes', 'reviews', 'bookmarks')
    try:
        for data in data_types:
            logging.debug(f'Generate data: {data}, TOTAL_GENRATE_DATA: {TOTAL_GENERATE_DATA}')
            b = 0
            for batch in data_generator.generate_data(data):
                b += len(batch)
                logging.debug(f'Insert data {b}/{TOTAL_GENERATE_DATA}')
                pg_loader.insert_data(batch, table_name=data)
    finally:
        pg_loader.close_cursor()


@measure_time('Чтение списка лайков')
def read_data_likes(connection):
    """
    Чтение списка лайков и измерение времени исполнения запроса
    """
    pg_reader = PostgresConnector(connection)
    try:
        query = 'SELECT * FROM likes WHERE rating=0;'
        likes_rows = pg_reader.fetch_data(query)
        logging.info(f'Лайки: {len(likes_rows)}')
    finally:
        pg_reader.close_cursor()


@measure_time('Чтение списка дизлайков')
def read_data_dislikes(connection):
    """
    Чтение списка дизлайков и измерение времени исполнения запроса
    """
    pg_reader = PostgresConnector(connection)
    try:
        query = 'SELECT * FROM likes WHERE rating=10;'
        dislikes_rows = pg_reader.fetch_data(query)
        logging.info(f'Дизлайки: {len(dislikes_rows)}')
    finally:
        pg_reader.close_cursor()


@measure_time('Чтение списка лайков и дизлайков у определенного фильма')
def read_data_film_likes(connection, select_film):
    """
    Чтение списка лайков и дизлайков у определенного фильма и измерение времени исполнения запроса
    """
    pg_reader = PostgresConnector(connection)
    try:
        query = f"SELECT * FROM likes where movie_id='{select_film}'"
        rows = pg_reader.fetch_data(query)
        likes = [row for row in rows if row[3] == 0]
        dislikes = [row for row in rows if row[3] == 10]

        logging.info(f'Дизлайки фильма "{select_film}": {len(dislikes)}')
        logging.info(f'Лайки фильма "{select_film}": {len(likes)}')
    finally:
        pg_reader.close_cursor()


@measure_time('Чтение списка ревью у определенного фильма')
def read_data_film_reviews(connection, select_film):
    """
    Чтение списка ревью у определенного фильма и измерение времени исполнения запроса
    """
    pg_reader = PostgresConnector(connection)
    try:
        query = f"SELECT * FROM reviews where movie_id='{select_film}'"
        rows = pg_reader.fetch_data(query)

        logging.info(f'Количество ревью фильма "{select_film}": {len(rows)}')
    finally:
        pg_reader.close_cursor()


@measure_time('Чтение средней оценки определенного фильма')
def read_data_film_avg_rating(connection, select_film):
    """
    Чтение средней оценки фильма и измерение времени исполнения запроса
    """
    pg_reader = PostgresConnector(connection)
    try:
        query = f"SELECT * FROM likes where movie_id='{select_film}'"
        rows = pg_reader.fetch_data(query)
        rating = [row[3] for row in rows]

        avg_rating = round(sum(rating)/len(rating), 2)
        logging.info(f'Средняя оценка фильма "{select_film}": {avg_rating}')
    finally:
        pg_reader.close_cursor()


@measure_time('Чтение списка закладок определенного фильма')
def read_data_film_bookmarks(connection, select_film):
    """
    Чтение списка закладок фильма и измерение времени исполнения запроса
    """
    pg_reader = PostgresConnector(connection)
    try:
        query = f"SELECT * FROM bookmarks where movie_id='{select_film}'"
        rows = pg_reader.fetch_data(query)

        logging.info(f'Количество закладок фильма "{select_film}": {len(rows)}')
    finally:
        pg_reader.close_cursor()


if __name__ == '__main__':
    logging.debug(f'Подключение к базе данных: {DSL}')
    with psycopg2.connect(**DSL) as connection:
        load_data(connection)
        read_data_likes(connection)
        read_data_dislikes(connection)
        read_data_film_likes(connection, get_film(connection, 'likes'))
        read_data_film_reviews(connection, get_film(connection, 'reviews'))
        read_data_film_avg_rating(connection, get_film(connection, 'likes'))
        read_data_film_bookmarks(connection, get_film(connection, 'bookmarks'))
        for result in output_result():
            logging.info(result)
