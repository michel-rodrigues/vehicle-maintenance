from datetime import datetime, timezone, timedelta

import pytest

from src.database.connection import db_connection
from src.models import Service, MaintenanceItem, ServiceItem
from src.repositories import RegistredVehicleRepository, MaintenanceCatalogRepository


@pytest.mark.usefixtures("setup_vehicle_table", "setup_registred_vehicles_table", "setup_services_items_table")
async def test_get_registred_vehicle():
    async with db_connection() as con:
        cur = await con.cursor()
        await cur.execute(
            """
            INSERT INTO vehicles VALUES
                ('Honda Fit 2015', 'Honda', 'Fit', '2015')
        """
        )
        await cur.execute(
            """
            INSERT INTO registred_vehicles VALUES
                ('ABC1A10', 'Honda Fit 2015')
        """
        )
        await cur.execute(
            """
            INSERT INTO services_items VALUES
                ('engine_oil_replacement', 10000, 10, '2024-01-02T02:55:10.369639+00:00', 'ABC1A10'),
                ('engine_oil_replacement', 20000, 18, '2024-08-23T02:55:10.369639+00:00', 'ABC1A10'),
                ('engine_oil_filter_replacement', 10000, 10, '2024-01-02T02:55:10.369639+00:00', 'ABC1A10')
        """
        )

    registred_vehicle = await RegistredVehicleRepository().get(plate="ABC1A10")

    assert registred_vehicle.plate == "ABC1A10"
    assert registred_vehicle.vehicle.manufacturer == "Honda"
    assert registred_vehicle.vehicle.model == "Fit"
    assert registred_vehicle.vehicle.year == "2015"
    services = registred_vehicle._services
    assert len(services) == 2
    assert len(services[Service.ENGINE_OIL_REPLACEMENT]) == 2
    assert len(services[Service.ENGINE_OIL_FILTER_REPLACEMENT]) == 1
    service_per_item = services[Service.ENGINE_OIL_REPLACEMENT]._items[0]
    assert service_per_item.service_date == datetime.fromisoformat("2024-01-02T02:55:10.369639+00:00")


@pytest.mark.usefixtures("setup_vehicle_table", "setup_registred_vehicles_table", "setup_services_items_table")
async def test_persist_new_registred_vehicle(registred_vehicle):
    repository = RegistredVehicleRepository()
    await repository.add(registred_vehicle)

    registred_vehicle = await repository.get(plate="ABC1A10")
    assert registred_vehicle.plate == "ABC1A10"
    assert registred_vehicle.vehicle.manufacturer == "Honda"
    assert registred_vehicle.vehicle.model == "Fit"
    assert registred_vehicle.vehicle.year == "2015"
    assert len(registred_vehicle._services) == 0


@pytest.mark.usefixtures("setup_vehicle_table", "setup_registred_vehicles_table", "setup_services_items_table")
async def test_update_persisted_registred_vehicle(registred_vehicle):
    await registred_vehicle.maintenance_performed(
        [
            ServiceItem(
                service=Service.ENGINE_OIL_REPLACEMENT,
                kilometrage=10_000,
                months_since_vehicle_release=8,
                service_date=datetime.now(tz=timezone.utc) - timedelta(weeks=24),
            ),
            ServiceItem(
                service=Service.ENGINE_OIL_REPLACEMENT,
                kilometrage=20_000,
                months_since_vehicle_release=14,
                service_date=datetime.now(tz=timezone.utc) - timedelta(weeks=48),
            ),
            ServiceItem(
                service=Service.BRAKE_FLUID_REPLACEMENT,
                kilometrage=25_000,
                months_since_vehicle_release=14,
                service_date=datetime.now(tz=timezone.utc),
            ),
        ]
    )
    repository = RegistredVehicleRepository()
    await repository.add(registred_vehicle)

    new_service_item = ServiceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=30_000,
        months_since_vehicle_release=22,
        service_date=datetime.now(tz=timezone.utc),
    )
    repository = RegistredVehicleRepository()
    registred_vehicle = await repository.get(plate="ABC1A10")
    await registred_vehicle.maintenance_performed([new_service_item])
    await repository.add(registred_vehicle)

    registred_vehicle = await repository.get(plate="ABC1A10")
    assert registred_vehicle.plate == "ABC1A10"
    assert registred_vehicle.vehicle.manufacturer == "Honda"
    assert registred_vehicle.vehicle.model == "Fit"
    assert registred_vehicle.vehicle.year == "2015"
    services = registred_vehicle._services
    assert len(services) == 2
    assert len(services[Service.ENGINE_OIL_REPLACEMENT]) == 3
    assert len(services[Service.BRAKE_FLUID_REPLACEMENT]) == 1


@pytest.mark.usefixtures("setup_maintenance_items_table")
async def test_get_maintenance_catalog():
    async with db_connection() as con:
        cur = await con.cursor()
        await cur.execute(
            """
            INSERT INTO maintenance_items VALUES
                ('engine_oil_replacement', '10000', '12', 'Honda Fit 2015'),
                ('engine_oil_filter_replacement', '10000', '12', 'Honda Fit 2015')
        """
        )

    expected_maintenance_items = [
        MaintenanceItem(
            service=Service.ENGINE_OIL_REPLACEMENT,
            kilometrage=10_000,
            month_interval=12,
        ),
        MaintenanceItem(
            service=Service.ENGINE_OIL_FILTER_REPLACEMENT,
            kilometrage=10_000,
            month_interval=12,
        ),
    ]

    maintenance_catalog = await MaintenanceCatalogRepository().get(vehicle_id="Honda Fit 2015")
    assert list(maintenance_catalog) == expected_maintenance_items
