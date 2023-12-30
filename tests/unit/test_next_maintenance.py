from datetime import datetime, timezone, timedelta

from src.models import (
    ServiceItem,
    ServicesPerItem,
    Service,
    NextServiceItem,
)


def test_should_register_new_services_per_item(registred_vehicle_with_one_item_catalog):
    last_service_item_performed = ServiceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=20_000,
        months_since_vehicle_release=14,
        service_date=datetime.now(tz=timezone.utc),
    )
    registred_vehicle_with_one_item_catalog.maintenance_performed([last_service_item_performed])

    services_per_item = registred_vehicle_with_one_item_catalog._services[last_service_item_performed.service]
    assert len(services_per_item) == 1
    assert services_per_item._items[0] == last_service_item_performed


def test_should_accumulate_service_items(registred_vehicle_with_one_item_catalog):
    service_item = ServiceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=10_000,
        months_since_vehicle_release=8,
        service_date=datetime.now(tz=timezone.utc) - timedelta(weeks=24),
    )
    services_per_item = ServicesPerItem()
    services_per_item.add(service_item)
    registred_vehicle_with_one_item_catalog._services[service_item.service] = services_per_item

    last_service_item_performed = ServiceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=20_000,
        months_since_vehicle_release=14,
        service_date=datetime.now(tz=timezone.utc),
    )
    registred_vehicle_with_one_item_catalog.maintenance_performed([last_service_item_performed])

    services_per_item = registred_vehicle_with_one_item_catalog._services[service_item.service]
    assert len(services_per_item) == 2
    assert services_per_item._items[0] == service_item
    assert services_per_item._items[1] == last_service_item_performed


def test_should_calculate_next_maintenace(registred_vehicle_with_one_item_catalog):
    last_service_item = ServiceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=20_000,
        months_since_vehicle_release=14,
        service_date=datetime.now(tz=timezone.utc),
    )
    registred_vehicle_with_one_item_catalog.maintenance_performed([last_service_item])

    expected_next_service_item = NextServiceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=30_000,
        months_since_vehicle_release=26,
    )

    next_maintenace = registred_vehicle_with_one_item_catalog.next_maintenance()
    assert len(next_maintenace) == 1
    assert next_maintenace[0] == expected_next_service_item


def test_should_include_maintenances_never_perfomed_before(registred_vehicle_with_two_items_catalog):
    last_service_item = ServiceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=20_000,
        months_since_vehicle_release=14,
        service_date=datetime.now(tz=timezone.utc),
    )
    registred_vehicle_with_two_items_catalog.maintenance_performed([last_service_item])

    expected_next_service_item = NextServiceItem(
        service=Service.ENGINE_OIL_FILTER_REPLACEMENT,
        kilometrage=10_000,
        months_since_vehicle_release=12,
    )

    next_maintenace = registred_vehicle_with_two_items_catalog.next_maintenance()
    assert len(next_maintenace) == 2
    assert next_maintenace[1] == expected_next_service_item
