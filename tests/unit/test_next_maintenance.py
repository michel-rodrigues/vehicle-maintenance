from datetime import datetime, timezone, timedelta

from src.models import (
    ItemMaintenance,
    MaintenanceCatalog,
    Vehicle,
    ItemService,
    ServicesPerItem,
    VehicleRegistration,
    Service,
    NextItemService,
)


def test_should_calculate_next_maintenace():
    item_maintenance = ItemMaintenance(
        service=Service.MOTOR_OIL_REPLACEMENT,
        kilometrage=10_000,
        month_interval=12,
    )
    maintenance_catalog = MaintenanceCatalog()
    maintenance_catalog.add(item_maintenance)
    vehicle = Vehicle(
        manufacturer="Honda",
        model="Fit",
        year=2015,
        maintenance_catalog=maintenance_catalog,
    )

    last_item_service = ItemService(
        service=Service.MOTOR_OIL_REPLACEMENT,
        kilometrage=20_000,
        months_since_vehicle_release=14,
        service_date=datetime.now(tz=timezone.utc),
    )
    services_per_item = ServicesPerItem()
    services_per_item.add(last_item_service)
    vehicle_registration = VehicleRegistration(
        plate="ABC1A10",
        vehicle=vehicle,
    )
    vehicle_registration.maintenance_performed([last_item_service])

    expected_next_item_service = NextItemService(
        service=Service.MOTOR_OIL_REPLACEMENT,
        kilometrage=30_000,
        months_since_vehicle_release=26,
    )

    next_maintenace = vehicle_registration.next_maintenance()
    assert next_maintenace[0] == expected_next_item_service
    assert next_maintenace[0].kilometrage == 30_000
    assert next_maintenace[0].months_since_vehicle_release == 26


def test_should_register_maintenance_items():
    item_maintenance = ItemMaintenance(
        service=Service.MOTOR_OIL_REPLACEMENT,
        kilometrage=10_000,
        month_interval=12,
    )
    maintenance_catalog = MaintenanceCatalog()
    maintenance_catalog.add(item_maintenance)
    vehicle = Vehicle(
        manufacturer="Honda",
        model="Fit",
        year=2015,
        maintenance_catalog=maintenance_catalog,
    )
    item_service = ItemService(
        service=Service.MOTOR_OIL_REPLACEMENT,
        kilometrage=10_000,
        months_since_vehicle_release=8,
        service_date=datetime.now(tz=timezone.utc) - timedelta(weeks=24),
    )
    vehicle_registration = VehicleRegistration(
        plate="ABC1A10",
        vehicle=vehicle,
    )
    services_per_item = ServicesPerItem()
    services_per_item.add(item_service)
    vehicle_registration._services[item_service.service] = services_per_item

    last_item_service_performed = ItemService(
        service=Service.MOTOR_OIL_REPLACEMENT,
        kilometrage=20_000,
        months_since_vehicle_release=14,
        service_date=datetime.now(tz=timezone.utc),
    )
    vehicle_registration.maintenance_performed([last_item_service_performed])

    services_per_item = vehicle_registration._services[item_service.service]
    assert len(services_per_item) == 2
    assert services_per_item._items[0] == item_service
    assert services_per_item._items[1] == last_item_service_performed


def test_should_register_new_services_per_item():
    item_maintenance = ItemMaintenance(
        service=Service.MOTOR_OIL_REPLACEMENT,
        kilometrage=10_000,
        month_interval=12,
    )
    maintenance_catalog = MaintenanceCatalog()
    maintenance_catalog.add(item_maintenance)
    vehicle = Vehicle(
        manufacturer="Honda",
        model="Fit",
        year=2015,
        maintenance_catalog=maintenance_catalog,
    )
    vehicle_registration = VehicleRegistration(
        plate="ABC1A10",
        vehicle=vehicle,
    )
    last_item_service_performed = ItemService(
        service=Service.MOTOR_OIL_REPLACEMENT,
        kilometrage=20_000,
        months_since_vehicle_release=14,
        service_date=datetime.now(tz=timezone.utc),
    )
    vehicle_registration.maintenance_performed([last_item_service_performed])

    services_per_item = vehicle_registration._services[last_item_service_performed.service]
    assert len(services_per_item) == 1
    assert services_per_item._items[0] == last_item_service_performed
