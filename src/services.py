from src.models import NextMaintenance
from src.repositories import RegistredVehicleRepository, MaintenanceCatalogRepository


def calculate_next_maintenace(
    plate: str,
    registered_vehicle_repository: RegistredVehicleRepository,
    maintenance_catalog_repository: MaintenanceCatalogRepository,
) -> NextMaintenance:
    registered_vehicle = registered_vehicle_repository.get(plate)
    maintenance_catalog = maintenance_catalog_repository.get(registered_vehicle.vehicle.id)
    return registered_vehicle.next_maintenance(maintenance_catalog)
