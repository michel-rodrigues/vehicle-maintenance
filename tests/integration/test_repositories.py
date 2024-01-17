from datetime import datetime, timezone, timedelta

import pytest

from src.models import Service, MaintenanceItem, ServiceItem, MaintenanceCatalog
from src.repositories import RegistredVehicleRepository, MaintenanceCatalogRepository, EmptyCatalogConstraint


@pytest.mark.usefixtures("setup_vehicle_table", "setup_registred_vehicles_table", "setup_services_items_table")
async def test_get_registred_vehicle(registred_vehicle):
    service_date = datetime.now(tz=timezone.utc) - timedelta(weeks=24)

    await registred_vehicle.maintenance_performed(
        [
            ServiceItem(
                service=Service.ENGINE_OIL_REPLACEMENT,
                kilometrage=10_000,
                months_since_vehicle_release=8,
                service_date=service_date,
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

    registred_vehicle = await RegistredVehicleRepository().get(plate="ABC1A10")

    assert registred_vehicle.plate == "ABC1A10"
    assert registred_vehicle.vehicle.manufacturer == "Honda"
    assert registred_vehicle.vehicle.model == "Fit"
    assert registred_vehicle.vehicle.year == "2015"
    services = registred_vehicle._services
    assert len(services) == 2
    assert len(services[Service.ENGINE_OIL_REPLACEMENT]) == 2
    assert len(services[Service.BRAKE_FLUID_REPLACEMENT]) == 1
    service_per_item = services[Service.ENGINE_OIL_REPLACEMENT]._items[0]
    assert service_per_item.service_date == service_date


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
    services = registred_vehicle._services
    assert len(services) == 2
    assert len(services[Service.ENGINE_OIL_REPLACEMENT]) == 3
    assert len(services[Service.BRAKE_FLUID_REPLACEMENT]) == 1


@pytest.mark.usefixtures("setup_maintenance_items_table")
async def test_add_new_maintenance_catalog(registred_vehicle):
    maintenance_item = MaintenanceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=10_000,
        month_interval=12,
    )
    maintenance_catalog = MaintenanceCatalog(vehicle_id=registred_vehicle.vehicle.id)
    await maintenance_catalog.add_maintenance_item(maintenance_item)

    maintenance_catalog_repository = MaintenanceCatalogRepository()
    await maintenance_catalog_repository.add(maintenance_catalog)

    maintenance_catalog = await maintenance_catalog_repository.get(vehicle_id=registred_vehicle.vehicle.id)
    assert list(maintenance_catalog) == [maintenance_item]


@pytest.mark.usefixtures("setup_maintenance_items_table")
async def test_cannot_add_empty_maintenance_catalog(registred_vehicle):
    maintenance_catalog = MaintenanceCatalog(vehicle_id=registred_vehicle.vehicle.id)

    maintenance_catalog_repository = MaintenanceCatalogRepository()
    with pytest.raises(EmptyCatalogConstraint):
        await maintenance_catalog_repository.add(maintenance_catalog)
