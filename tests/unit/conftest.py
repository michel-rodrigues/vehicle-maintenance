import pytest

from src.models import (
    MaintenanceItem,
    MaintenanceCatalog,
    RegistredVehicle,
    Service,
    Vehicle,
)


@pytest.fixture
def registred_vehicle_with_one_item_catalog():
    maintenance_item = MaintenanceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=10_000,
        month_interval=12,
    )
    maintenance_catalog = MaintenanceCatalog()
    maintenance_catalog.add(maintenance_item)
    vehicle = Vehicle(
        manufacturer="Honda",
        model="Fit",
        year=2015,
        maintenance_catalog=maintenance_catalog,
    )
    return RegistredVehicle(plate="ABC1A10", vehicle=vehicle)


@pytest.fixture
def registred_vehicle_with_two_items_catalog():
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
    maintenance_catalog = MaintenanceCatalog()
    maintenance_catalog.add(maintenance_item_1)
    maintenance_catalog.add(maintenance_item_2)
    vehicle = Vehicle(
        manufacturer="Honda",
        model="Fit",
        year=2015,
        maintenance_catalog=maintenance_catalog,
    )
    return RegistredVehicle(plate="ABC1A10", vehicle=vehicle)
