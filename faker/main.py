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

NUMBER_OF_FILMS = 1
NUMBER_OF_PERSONS = 15

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
    time_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    data = {
        'id': str(uuid4()),
        'title': fake.sentence(nb_words=3),
        'description': fake.text(max_nb_chars=200),
        'imdb_rating': str(round(random.uniform(1.0, 10.0), 1)),
        'type': 'movie',
        'created': time_now,
        'modified': time_now,
    }
    return list(data.values())


def generate_person_data():
    time_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    data = {
        'id': str(uuid4()),
        'full_name': fake.name(),
        'created': time_now,
        'modified': time_now,
    }
    return list(data.values())

def generate_genre_data(genre, discription):
    time_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    data = {
        'id': str(uuid4()),
        'genre': genre,
        'description': discription,
        'created': time_now,
        'modified': time_now,
    }
    return list(data.values())

def generate_genre_film_data(genre_id, film_id):
    time_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    data = {
        'id': str(uuid4()),
        'genre_id': genre_id,
        'film_id': film_id,
        'created': time_now
    }
    return list(data.values())

def generate_person_film_data(person_id, film_id, role):
    time_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    data = {
        'id': str(uuid4()),
        'person_id': person_id,
        'film_id': film_id,
        'role': role,
        'created': time_now,
    }
    return list(data.values())

if __name__ == '__main__':
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            genres_list = [generate_genre_data(genre, disription) for genre, disription in GENRES.items()]
            genres_query = '\n'.join(['\t'.join(genre) for genre in genres_list])
            query = """
                    COPY content.genre (id, name, description, created, modified) FROM stdin; 
                    """
            cursor.copy_expert(query, StringIO(genres_query))
            
            persons_list = [generate_person_data() for x in range(NUMBER_OF_PERSONS)]
            persons_query = '\n'.join(['\t'.join(person) for person in persons_list])
            
            query = """
                    COPY content.person (id, full_name, created, modified) FROM stdin; 
                    """
            cursor.copy_expert(query, StringIO(persons_query))
            conn.commit()
            
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
                    genres_films_list.append(generate_genre_film_data(genre[0], film[0]))
                for actor in actors:
                    persons_films_list.append(generate_person_film_data(actor[0], film[0], 'actor'))
                for director in directors:
                    persons_films_list.append(generate_person_film_data(director[0], film[0], 'director'))
                for writer in writers:
                    persons_films_list.append(generate_person_film_data(writer[0], film[0], 'writer'))
                    
            films_string = '\n'.join(['\t'.join(film) for film in films_list])
            genres_films_string = '\n'.join(['\t'.join(genre) for genre in genres_films_list])
            persons_films_string = '\n'.join(['\t'.join(person) for person in persons_films_list])
            
            query_film = """
                COPY content.film_work (id, title, description, rating, type, created, modified) FROM stdin;
            """
            query_genre_film = """
                COPY content.genre_film_work (id, genre_id, film_work_id, created) FROM stdin;
            """
            query_person_film = """
                COPY content.person_film_work (id, person_id, film_work_id, role, created) FROM stdin;
            """
            
            cursor.copy_expert(query_film, StringIO(films_string))
            cursor.copy_expert(query_genre_film, StringIO(genres_films_string))
            cursor.copy_expert(query_person_film, StringIO(persons_films_string))
            
            conn.commit()
