from datetime import datetime, timezone

import pytest

from src.models import Service
from src.repositories import RegistredVehicleRepository


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
