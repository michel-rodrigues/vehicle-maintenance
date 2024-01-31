from datetime import datetime, timezone

from src.models import ServiceItem, Service, NextServiceItem, RegistredVehicle, MaintenanceCatalog
from src.repositories import RegistredVehicleRepository, MaintenanceCatalogRepository
from src.services import calculate_next_maintenace


class FakeRegisteredVehicleRepository(RegistredVehicleRepository):
    def __init__(self, registred_vehicle: RegistredVehicle):
        self.registred_vehicle = registred_vehicle

    async def get(self, plate: str):
        assert self.registred_vehicle.plate == plate
        return self.registred_vehicle


class FakeMaintenanceCatalogRepository(MaintenanceCatalogRepository):
    def __init__(self, maintenance_catalog: MaintenanceCatalog):
        self.maintenance_catalog = maintenance_catalog

    async def get(self, vehicle_id: str):
        assert self.maintenance_catalog.vehicle_id == vehicle_id
        return self.maintenance_catalog


async def test_it_should_calculate_next_maintenace(registred_vehicle, one_item_catalog):
    last_service_item = ServiceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=20_000,
        months_since_vehicle_release=14,
        service_date=datetime.now(tz=timezone.utc),
    )
    await registred_vehicle.maintenance_performed([last_service_item])
    registered_vehicle_repository = FakeRegisteredVehicleRepository(registred_vehicle)

    maintenance_catalog_repository = FakeMaintenanceCatalogRepository(one_item_catalog)

    expected_next_service_item = NextServiceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=30_000,
        months_since_vehicle_release=26,
    )

    next_maintenace = await calculate_next_maintenace(
        registred_vehicle.plate,
        registered_vehicle_repository,
        maintenance_catalog_repository,
    )
    assert len(next_maintenace) == 1
    assert next_maintenace[0] == expected_next_service_item


async def test_it_should_include_maintenances_never_perfomed_before(registred_vehicle, three_items_catalog):
    await registred_vehicle.maintenance_performed(
        [
            ServiceItem(
                service=Service.ENGINE_OIL_REPLACEMENT,
                kilometrage=20_000,
                months_since_vehicle_release=14,
                service_date=datetime.now(tz=timezone.utc),
            ),
            ServiceItem(
                service=Service.FUEL_FILTER_REPLACEMENT,
                kilometrage=20_000,
                months_since_vehicle_release=14,
                service_date=datetime.now(tz=timezone.utc),
            ),
        ]
    )

    registered_vehicle_repository = FakeRegisteredVehicleRepository(registred_vehicle)

    maintenance_catalog_repository = FakeMaintenanceCatalogRepository(three_items_catalog)

    expected_next_service_item = NextServiceItem(
        service=Service.INSPECT_BATTERY_CHARGE_CAPACITY,
        months_since_vehicle_release=12,
    )

    next_maintenace = await calculate_next_maintenace(
        registred_vehicle.plate,
        registered_vehicle_repository,
        maintenance_catalog_repository,
    )
    assert len(next_maintenace) == 3
    assert next_maintenace[2] == expected_next_service_item
