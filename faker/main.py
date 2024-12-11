from faker import Faker
import random
from uuid import uuid4
from datetime import datetime, timezone
from config import DBConfig
import psycopg2
from psycopg2.extras import DictCursor
from io import StringIO


fake = Faker()
db_config = DBConfig()

DB_CONFIG = {
    'dbname': db_config.database,
    'user': db_config.username,
    'password': db_config.password,
    'host': db_config.host,
    'port': db_config.port,
}

NUMBER_OF_FILMS = 200000
NUMBER_OF_PERSONS = 4000
TIME_NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")

GENRES = {
    'Action': 'Action movies',
    'Adventure': 'Adventure',
    'Fantasy': 'Fantasy movies',
    'Sci-Fi': 'Sci-Fi movies',
    'Drama': 'Drama movies',
    'Music': 'Music movies',
    'Romance': 'Romance movies',
    'Thriller': 'Thriller movies',
    'Mystery': 'Mystery movies',
    'Comedy': 'Comedy movies',
    'Animation': 'Animation movies',
    'Family': 'Family movies',
    'Biography': 'Biography movies',
    'Musical': 'Musical movies',
    'Crime': 'Crime movies',
    'Short': 'Short movies',
    'Western': 'Western movies',
    'Documentary': 'Documentary movies',
    'History': 'History movies',
    'War': 'War mmvies',
    'Game-Show': 'Game-Show mmvies',
    'Reality-TV': 'Reality-TV mmvies',
    'Horror': 'Horror mmvies',
    'Sport': 'Sport mmvies',
    'Talk-Show': 'Talk-Show mmvies',
    'News': 'News mmvies',
}

ROLES = [
    'actor',
    'writer',
    'director',
]


def generate_films_data():
    id = str(uuid4())
    title = fake.sentence(nb_words=3)
    description = fake.text(max_nb_chars=200).replace('\n', '')
    rating = str(round(random.uniform(1.0,10.0), 1))
    type = 'movie'
    created = TIME_NOW
    modified = TIME_NOW
    return [id, title, description, rating, type, created, modified]


def generate_person_data():
    id = str(uuid4())
    full_name = fake.name()
    created = TIME_NOW
    modified = TIME_NOW
    return [id, full_name, created, modified]


def generate_genre_data(genre, description):
    id = str(uuid4())
    created = TIME_NOW
    modified = TIME_NOW
    return [id, genre, description, created, modified]


def generate_genre_film_relation(genre_id, film_id):
    id = str(uuid4())
    created = TIME_NOW
    return [id, genre_id, film_id, created]


def generate_person_film_relation(person_id, film_id, role):
    id = str(uuid4())
    created = TIME_NOW
    return [id, person_id, film_id, role, created]


def copy_query(conn: psycopg2.connect, cursor: DictCursor, table: str, fields: str, copy_data: str):
    query = f"""
            COPY content.{table} {fields} FROM stdin;
            """
    cursor.copy_expert(query, StringIO(copy_data))
    return conn.commit()


if __name__ == '__main__':
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            
            genres_list = [generate_genre_data(genre, disription) for genre, disription in GENRES.items()]
            genres_query = '\n'.join(['\t'.join(genre) for genre in genres_list])     
            copy_query(conn=conn,
                       cursor=cursor,
                       table='genre',
                       fields='(id, name, description, created, modified)',
                       copy_data=genres_query)
            
            persons_list = [generate_person_data() for x in range(NUMBER_OF_PERSONS)]
            persons_query = '\n'.join(['\t'.join(person) for person in persons_list])
            copy_query(conn=conn,
                       cursor=cursor,
                       table='person',
                       fields='(id, full_name, created, modified)',
                       copy_data=persons_query)
            
            films_list = []
            genres_films_list = []
            persons_films_list = []
            for film_number in range(NUMBER_OF_FILMS):
                genre_film = random.sample(genres_list, random.randint(1,2))
                actors = random.sample(persons_list, random.randint(1,6))
                directors = random.sample(persons_list, random.randint(1,2))
                writers = random.sample(persons_list, random.randint(1,2))
                film = generate_films_data()
                films_list.append(film)
                for genre in genre_film:
                    genres_films_list.append(generate_genre_film_relation(genre[0], film[0]))
                for actor in actors:
                    persons_films_list.append(generate_person_film_relation(actor[0], film[0], 'actor'))
                for director in directors:
                    persons_films_list.append(generate_person_film_relation(director[0], film[0], 'director'))
                for writer in writers:
                    persons_films_list.append(generate_person_film_relation(writer[0], film[0], 'writer'))
                    
            films_string = '\n'.join(['\t'.join(film) for film in films_list])
            genres_films_string = '\n'.join(['\t'.join(genre) for genre in genres_films_list])
            persons_films_string = '\n'.join(['\t'.join(person) for person in persons_films_list])
            
            copy_query(conn=conn,
                       cursor=cursor,
                       table='film_work',
                       fields='(id, title, description, rating, type, created, modified)',
                       copy_data=films_string)
            copy_query(conn=conn,
                       cursor=cursor,
                       table='genre_film_work',
                       fields='(id, genre_id, film_work_id, created)',
                       copy_data=genres_films_string)
            copy_query(conn=conn,
                       cursor=cursor,
                       table='person_film_work',
                       fields='(id, person_id, film_work_id, role, created)',
                       copy_data=persons_films_string)
