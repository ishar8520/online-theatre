import argparse
import logging

from clickhouse_driver import Client
from helpers import generate_batched_events, measure_time


def parse_args():
    parser = argparse.ArgumentParser(description='Generate and process events.')
    parser.add_argument('--total', type=int, default=100000, help='Total number of events to generate.')
    parser.add_argument('--batch_size', type=int, default=1000, help='Batch size for generating events.')
    return parser.parse_args()


@measure_time('Вставка')
def transform_data(event_generator, insert_events, total):
    """Преобразование данных и вставка в БД"""
    for batch in event_generator:
        values = [
            (
                event['type'],
                event['timestamp'],
                event['user_id'],
                event['fingerprint'],
                event['element'],
                event['url'],
            )
            for event in batch
        ]
        insert_events(values)


def insert_events(values):
    client.execute(
        """INSERT INTO event (type, timestamp, user_id, fingerprint, element, url)
            VALUES """,
        values,
    )


@measure_time('Чтение')
def get_events(total):
    client.execute(f"""SELECT * FROM event LIMIT {total}""")


@measure_time('Обновление')
def update_events(total):
    client.execute(
        f"""ALTER TABLE event UPDATE element = 'pic' 
                WHERE id in (SELECT id FROM event ORDER BY id LIMIT {total})"""
    )


def drop_events():
    client.execute("""DROP TABLE IF EXISTS event""")


def main(total=100000, batch_size=100000):
    global client
    client = Client(host='localhost')
    logging.warning('Создаю базу данных')
    client.execute('CREATE DATABASE IF NOT EXISTS example ON CLUSTER company_cluster')
    drop_events()
    logging.warning('Создаю таблицы')
    client.execute(
        """
        CREATE TABLE IF NOT EXISTS event (
            id UInt32,
            type VARCHAR NOT NULL,
            timestamp VARCHAR,
            user_id VARCHAR NOT NULL,
            fingerprint VARCHAR(256) NOT NULL,
            element VARCHAR NOT NULL,
            url VARCHAR NOT NULL)
            ENGINE = MergeTree
            PRIMARY KEY id;"""
    )
    logging.warning('Создаю ивенты')
    event_generator = generate_batched_events(count=total, batch_size=batch_size)
    transform_data(event_generator, insert_events, total=total)
    get_events(total=total)
    update_events(total=total)
    drop_events()


if __name__ == '__main__':
    args = parse_args()
    main(total=args.total, batch_size=args.batch_size)

