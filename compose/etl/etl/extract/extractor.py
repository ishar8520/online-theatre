from __future__ import annotations

from collections.abc import Iterable

import backoff
import psycopg
import psycopg.abc
import psycopg.rows

from .query import (
    ExtractSQLStatement,
    ExtractFilmWorksSQLStatement,
)
from .state import LastModified


class PostgreSQLConnectionFactory:
    connection_params: dict

    def __init__(self, *, connection_params: dict) -> None:
        self.connection_params = connection_params

    @backoff.on_exception(backoff.expo, psycopg.OperationalError)
    def create(self) -> psycopg.Connection[dict]:
        return psycopg.connect(**self.connection_params, row_factory=psycopg.rows.dict_row)


class PostgreSQLCursorExecutor:
    cursor: psycopg.Cursor[dict]

    def __init__(self, *, cursor: psycopg.Cursor[dict]) -> None:
        self.cursor = cursor

    @backoff.on_exception(backoff.expo, psycopg.OperationalError)
    def execute(self,
                *,
                query: psycopg.abc.Query,
                params: psycopg.abc.Params | None = None) -> psycopg.Cursor[dict]:
        return self.cursor.execute(query, params)


class FilmWorksExtractor:
    connection_factory: PostgreSQLConnectionFactory
    extract_sql_statement: ExtractSQLStatement

    def __init__(self, *, connection_params: dict, batch_size: int | None = None) -> None:
        self.connection_factory = PostgreSQLConnectionFactory(connection_params=connection_params)
        self.extract_sql_statement = ExtractFilmWorksSQLStatement(batch_size=batch_size or 100)

    def extract(self, *, last_modified: LastModified) -> Iterable[dict]:
        with self.connection_factory.create() as connection:
            with connection.cursor() as cursor:
                cursor_executor = PostgreSQLCursorExecutor(cursor=cursor)
                query = self.extract_sql_statement.compile(last_modified=last_modified)
                yield from cursor_executor.execute(query=query)
