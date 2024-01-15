import os

import aiosqlite
import sqlite3
from contextlib import asynccontextmanager
from sqlite3 import Connection


@asynccontextmanager
async def db_connection() -> Connection:
    connection = await aiosqlite.connect(os.environ.get("DATABASE", "database.db"), detect_types=sqlite3.PARSE_COLNAMES)
    connection.row_factory = aiosqlite.Row
    try:
        yield connection
        await connection.commit()
    finally:
        await connection.close()
