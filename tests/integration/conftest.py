import pytest

from src.database.connection import db_connection
from src.database.tables import (
    create_vehicle_table,
    create_registred_vehicles_table,
    create_services_items_table,
    create_maintenance_items_table,
)


@pytest.fixture
async def setup_vehicle_table():
    async with db_connection() as con:
        await con.execute("DROP TABLE IF EXISTS vehicles;")
        await create_vehicle_table(con)


@pytest.fixture
async def setup_registred_vehicles_table():
    async with db_connection() as con:
        await con.execute("DROP TABLE IF EXISTS registred_vehicles;")
        await create_registred_vehicles_table(con)


@pytest.fixture
async def setup_services_items_table():
    async with db_connection() as con:
        await con.execute("DROP TABLE IF EXISTS services_items;")
        await create_services_items_table(con)


@pytest.fixture
async def setup_maintenance_items_table():
    async with db_connection() as con:
        await con.execute("DROP TABLE IF EXISTS maintenance_items;")
        await create_maintenance_items_table(con)
