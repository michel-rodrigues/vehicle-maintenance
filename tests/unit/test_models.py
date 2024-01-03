from datetime import datetime, timezone, timedelta

from src.models import (
    ServiceItem,
    ServicesPerItem,
    Service,
)


async def test_should_register_new_services_per_item(registred_vehicle):
    last_service_item_performed = ServiceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=20_000,
        months_since_vehicle_release=14,
        service_date=datetime.now(tz=timezone.utc),
    )
    await registred_vehicle.maintenance_performed([last_service_item_performed])

    services_per_item = registred_vehicle._services[last_service_item_performed.service]
    assert len(services_per_item) == 1
    assert services_per_item._items[0] == last_service_item_performed


async def test_should_accumulate_service_items(registred_vehicle):
    service_item = ServiceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=10_000,
        months_since_vehicle_release=8,
        service_date=datetime.now(tz=timezone.utc) - timedelta(weeks=24),
    )
    services_per_item = ServicesPerItem()
    await services_per_item.add(service_item)
    registred_vehicle._services[service_item.service] = services_per_item

    last_service_item_performed = ServiceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=20_000,
        months_since_vehicle_release=14,
        service_date=datetime.now(tz=timezone.utc),
    )
    await registred_vehicle.maintenance_performed([last_service_item_performed])

    services_per_item = registred_vehicle._services[service_item.service]
    assert len(services_per_item) == 2
    assert services_per_item._items[0] == service_item
    assert services_per_item._items[1] == last_service_item_performed
