import sqlite3
from contextlib import contextmanager
from sqlite3 import Connection


@contextmanager
def db_connection(self) -> Connection:
    connection = self._sqlite_connection or sqlite3.connect("database.db", detect_types=sqlite3.PARSE_COLNAMES)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()
