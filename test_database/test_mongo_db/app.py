import psycopg2
from common.constants import DSL, TOTAL_GENERATE_DATA
from common.data_connector import PostgresConnector
from common.data_generator import GenerateData


def load_data(pg_conn):
    pg_loader = PostgresConnector(pg_conn)
    data_generator = GenerateData(TOTAL_GENERATE_DATA)
    data_types = ("like", "review", "bookmark")
    try:
        for data in data_types:
            for batch in data_generator.generate_data(data):
                pg_loader.insert_data(batch, table_name=data)
    finally:
        pg_loader.close_cursor()


if __name__ == "__main__":
    with psycopg2.connect(*DSL) as pg_conn:
        load_data(pg_conn)
