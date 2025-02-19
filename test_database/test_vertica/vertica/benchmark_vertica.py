import argparse
import logging

import vertica_python
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



def insert_events_copy(values):   
    data_str = "\n".join(["|".join(map(str, row)) for row in values])
    cursor.copy("COPY event (type, timestamp, user_id, fingerprint, element, url) FROM STDIN DELIMITER '|' ", data_str)


def insert_events_executemany(values):
    cursor.executemany(
        """INSERT INTO event (type, timestamp, user_id, fingerprint, element, url)
            VALUES (%s, %s, %s, %s, %s, %s)""",
        values,
    )
    

@measure_time('Чтение')
def get_events(total):
    cursor.execute(f"""SELECT * FROM event LIMIT {total}""")


@measure_time('Обновление')
def update_events(total):
    # cursor.execute(
    #     f"""ALTER TABLE event UPDATE element = 'pic' 
    #             WHERE id in (SELECT id FROM event ORDER BY id LIMIT {total})"""
    # )
    cursor.execute(f"""
        MERGE INTO event USING (
            SELECT id FROM event ORDER BY id LIMIT {total}
        ) AS subquery
        ON event.id = subquery.id
        WHEN MATCHED THEN UPDATE SET element = 'pic'
    """)



def drop_events():
    cursor.execute("""DROP TABLE IF EXISTS event""")


def main(total=100000, batch_size=100000):
    conn_info = {
        'host': 'localhost',
        'port': 5433,
        'user': 'dbadmin',
        'password': '',
        'database': 'docker',
        'autocommit': True
    }
    with vertica_python.connect(**conn_info) as conn:
        global cursor
        cursor = conn.cursor()
        print("Подключение успешно!")
        drop_events()
        logging.warning('Создаю таблицы')
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS event (
                id INT,
                type VARCHAR NOT NULL,
                timestamp TIMESTAMP,
                user_id VARCHAR NOT NULL,
                fingerprint VARCHAR(256) NOT NULL,
                element VARCHAR NOT NULL,
                url VARCHAR NOT NULL)
                ORDER BY id;"""
        )
        logging.warning('Создаю ивенты')
        event_generator = generate_batched_events(count=total, batch_size=batch_size)
        transform_data(event_generator, insert_events_copy, total=total)
        # transform_data(event_generator, insert_events_executemany, total=total)
        get_events(total=total)
        update_events(total=total)
        drop_events()


if __name__ == '__main__':
    args = parse_args()
    main(total=args.total, batch_size=args.batch_size)

