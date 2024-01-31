import os

import pytest

from src.database.connection import db_connection
from src.database.tables import (
    create_vehicle_table,
    create_registred_vehicles_table,
    create_services_items_table,
    create_maintenance_items_table,
)
from src.models import (
    MaintenanceItem,
    MaintenanceCatalog,
    RegistredVehicle,
    Service,
    Vehicle,
)


@pytest.fixture(scope="session", autouse=True)
async def set_env():
    os.environ["DATABASE"] = "test.db"
    yield


@pytest.fixture
async def registred_vehicle() -> RegistredVehicle:
    vehicle = Vehicle(
        manufacturer="Honda",
        model="Fit",
        year=2015,
    )
    yield RegistredVehicle(plate="ABC1A10", vehicle=vehicle)


@pytest.fixture
async def one_item_catalog(registred_vehicle) -> MaintenanceCatalog:
    maintenance_item = MaintenanceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=10_000,
        month_interval=12,
    )
    maintenance_catalog = MaintenanceCatalog(vehicle_id=registred_vehicle.vehicle.id)
    await maintenance_catalog.add_maintenance_item(maintenance_item)
    yield maintenance_catalog


@pytest.fixture
async def three_items_catalog(registred_vehicle) -> MaintenanceCatalog:
    maintenance_item_1 = MaintenanceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=10_000,
        month_interval=12,
    )
    maintenance_item_2 = MaintenanceItem(
        service=Service.FUEL_FILTER_REPLACEMENT,
        kilometrage=10_000,
    )
    maintenance_item_3 = MaintenanceItem(
        service=Service.INSPECT_BATTERY_CHARGE_CAPACITY,
        month_interval=12,
    )
    maintenance_catalog = MaintenanceCatalog(vehicle_id=registred_vehicle.vehicle.id)
    await maintenance_catalog.add_maintenance_item(maintenance_item_1)
    await maintenance_catalog.add_maintenance_item(maintenance_item_2)
    await maintenance_catalog.add_maintenance_item(maintenance_item_3)
    yield maintenance_catalog


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
