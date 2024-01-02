import sqlite3
from contextlib import contextmanager
from datetime import datetime

from src.models import RegistredVehicle, Vehicle, ServiceItem, MaintenanceCatalog, MaintenanceItem, Service


def convert_datetime(val):
    """Convert ISO 8601 datetime to datetime.datetime object."""
    return datetime.fromisoformat(val.decode())


def convert_service(val):
    return Service(val.decode())


sqlite3.register_converter("datetime", convert_datetime)
sqlite3.register_converter("service", convert_service)


class SQLiteRepository:
    def __init__(self, sqlite_connection=None):
        self._sqlite_connection = sqlite_connection

    @contextmanager
    def _connection(self):
        connection = self._sqlite_connection or sqlite3.connect("database.db", detect_types=sqlite3.PARSE_COLNAMES)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()


class RegistredVehicleRepository(SQLiteRepository):
    def get(self, plate: str) -> RegistredVehicle:
        with self._connection() as connection:
            query = """
                SELECT *
                FROM registred_vehicles as rv
                INNER JOIN vehicles as v
                    ON rv.vehicle_id = v.id
                WHERE rv.plate = :plate
            """
            result = connection.execute(query, {"plate": plate})
            row = result.fetchone()
            vehicle = Vehicle(manufacturer=row["manufacturer"], model=row["model"], year=row["year"])
            vehicle._id = row["id"]
            regitred_vehicle = RegistredVehicle(plate=row["plate"], vehicle=vehicle)

            query = """
                SELECT service, kilometrage, months_since_vehicle_release, service_date as "service_date [datetime]"
                FROM services_items
                WHERE vehicle_plate = :plate
            """
            regitred_vehicle.maintenance_performed(
                ServiceItem(
                    service=row["service"],
                    kilometrage=row["kilometrage"],
                    months_since_vehicle_release=row["months_since_vehicle_release"],
                    service_date=row["service_date"],
                )
                for row in connection.execute(query, {"plate": plate})
            )

        return regitred_vehicle


class MaintenanceCatalogRepository(SQLiteRepository):
    def get(self, vehicle_id: str) -> MaintenanceCatalog:
        maintenance_catalog = MaintenanceCatalog(vehicle_id)
        query = """
            SELECT kilometrage, month_interval, service AS "service [service]"
            FROM maintenance_items
            WHERE vehicle_id = :vehicle_id
        """
        with self._connection() as connection:
            for row in connection.execute(query, {"vehicle_id": vehicle_id}):
                maintenance_catalog.add_maintenance_item(
                    MaintenanceItem(
                        service=row["service"],
                        kilometrage=row["kilometrage"],
                        month_interval=row["month_interval"],
                    )
                )
        return maintenance_catalog
