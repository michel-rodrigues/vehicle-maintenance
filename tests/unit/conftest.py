import pytest

from src.models import (
    MaintenanceItem,
    MaintenanceCatalog,
    RegistredVehicle,
    Service,
    Vehicle,
)


@pytest.fixture
def registred_vehicle() -> RegistredVehicle:
    vehicle = Vehicle(
        manufacturer="Honda",
        model="Fit",
        year=2015,
    )
    return RegistredVehicle(plate="ABC1A10", vehicle=vehicle)


@pytest.fixture
def one_item_catalog(registred_vehicle) -> MaintenanceCatalog:
    maintenance_item = MaintenanceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=10_000,
        month_interval=12,
    )
    maintenance_catalog = MaintenanceCatalog(vehicle_id=registred_vehicle.vehicle.id)
    maintenance_catalog.add_maintenance_item(maintenance_item)
    return maintenance_catalog


@pytest.fixture
def two_items_catalog(registred_vehicle) -> MaintenanceCatalog:
    maintenance_item_1 = MaintenanceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=10_000,
        month_interval=12,
    )
    maintenance_item_2 = MaintenanceItem(
        service=Service.ENGINE_OIL_FILTER_REPLACEMENT,
        kilometrage=10_000,
        month_interval=12,
    )
    maintenance_catalog = MaintenanceCatalog(vehicle_id=registred_vehicle.vehicle.id)
    maintenance_catalog.add_maintenance_item(maintenance_item_1)
    maintenance_catalog.add_maintenance_item(maintenance_item_2)
    return maintenance_catalog
