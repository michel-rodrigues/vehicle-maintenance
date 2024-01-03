from src.models import NextMaintenance
from src.repositories import RegistredVehicleRepository, MaintenanceCatalogRepository


async def calculate_next_maintenace(
    plate: str,
    registered_vehicle_repository: RegistredVehicleRepository,
    maintenance_catalog_repository: MaintenanceCatalogRepository,
) -> NextMaintenance:
    registered_vehicle = await registered_vehicle_repository.get(plate)
    maintenance_catalog = await maintenance_catalog_repository.get(registered_vehicle.vehicle.id)
    return await registered_vehicle.next_maintenance(maintenance_catalog)
