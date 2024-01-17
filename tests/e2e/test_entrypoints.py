from datetime import datetime, timezone

import pytest

from src.models import Service, MaintenanceItem, MaintenanceCatalog
from src.repositories import RegistredVehicleRepository, MaintenanceCatalogRepository


@pytest.mark.usefixtures("setup_vehicle_table", "setup_registred_vehicles_table", "setup_services_items_table")
async def test_add_service_items(test_client, registred_vehicle):
    repository = RegistredVehicleRepository()
    await repository.add(registred_vehicle)
    payload = {
        "plate": registred_vehicle.plate,
        "service": Service.ENGINE_OIL_REPLACEMENT.value,
        "kilometrage": 20_000,
        "months_since_vehicle_release": 14,
        "service_date": datetime.now(tz=timezone.utc).isoformat(),
    }
    response = test_client.post("/registred-vehicles/{plate}/services-items", json=payload)
    assert response.status_code == 201
    assert registred_vehicle.plate == (await repository.get(plate="ABC1A10")).plate


@pytest.mark.usefixtures(
    "setup_vehicle_table",
    "setup_registred_vehicles_table",
    "setup_services_items_table",
    "setup_maintenance_items_table",
)
async def test_next_maintenance(test_client, registred_vehicle):
    registred_vehicle_repository = RegistredVehicleRepository()
    await registred_vehicle_repository.add(registred_vehicle)

    engine_oil_replacement = MaintenanceItem(
        service=Service.ENGINE_OIL_REPLACEMENT,
        kilometrage=10_000,
        month_interval=12,
    )
    engine_oil_filter_replacement = MaintenanceItem(
        service=Service.ENGINE_OIL_FILTER_REPLACEMENT,
        kilometrage=10_000,
        month_interval=12,
    )
    maintenance_catalog = MaintenanceCatalog(vehicle_id=registred_vehicle.vehicle.id)
    await maintenance_catalog.add_maintenance_item(engine_oil_replacement)
    await maintenance_catalog.add_maintenance_item(engine_oil_filter_replacement)
    maintenance_catalog_repository = MaintenanceCatalogRepository()
    await maintenance_catalog_repository.add(maintenance_catalog)

    expected_response = [
        {
            "service": engine_oil_replacement.service,
            "kilometrage": engine_oil_replacement.kilometrage,
            "months_since_vehicle_release": engine_oil_replacement.month_interval,
        },
        {
            "service": engine_oil_filter_replacement.service,
            "kilometrage": engine_oil_replacement.kilometrage,
            "months_since_vehicle_release": engine_oil_replacement.month_interval,
        },
    ]
    response = test_client.get(f"/registred-vehicles/{registred_vehicle.plate}/next-maintenance")
    assert response.status_code == 200
    assert response.json() == expected_response
