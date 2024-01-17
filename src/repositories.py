import os
from collections.abc import Iterable

import aiosqlite
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime

from src.models import RegistredVehicle, Vehicle, ServiceItem, MaintenanceCatalog, MaintenanceItem, Service


def convert_datetime(val):
    return datetime.fromisoformat(val.decode())


def convert_service(val):
    return Service(val.decode())


aiosqlite.register_converter("datetime", convert_datetime)
aiosqlite.register_converter("service", convert_service)


class SQLiteRepository:
    def __init__(self, sqlite_connection=None):
        self._sqlite_connection = sqlite_connection

    @asynccontextmanager
    async def _connection(self):
        connection = self._sqlite_connection or await aiosqlite.connect(
            os.environ.get("DATABASE", "database.db"),
            detect_types=sqlite3.PARSE_COLNAMES,
        )
        connection.row_factory = aiosqlite.Row
        try:
            yield connection
            await connection.commit()
        finally:
            await connection.close()


class RegistredVehicleRepository(SQLiteRepository):
    async def _get_registred_vehicle(self, plate: str, cursor):
        query = """
            SELECT *
            FROM registred_vehicles as rv
            INNER JOIN vehicles as v
                ON rv.vehicle_id = v.id
            WHERE rv.plate = :plate
        """
        result = await cursor.execute(query, {"plate": plate})
        row = await result.fetchone()
        vehicle = Vehicle(manufacturer=row["manufacturer"], model=row["model"], year=row["year"])
        vehicle._id = row["id"]
        return RegistredVehicle(plate=row["plate"], vehicle=vehicle)

    async def _fetch_service_items(self, plate: str, cursor):
        query = """
            SELECT service, kilometrage, months_since_vehicle_release, service_date as "service_date [datetime]"
            FROM services_items
            WHERE vehicle_plate = :plate
        """
        result = await cursor.execute(query, {"plate": plate})
        return (
            ServiceItem(
                service=row["service"],
                kilometrage=row["kilometrage"],
                months_since_vehicle_release=row["months_since_vehicle_release"],
                service_date=row["service_date"],
            )
            for row in await result.fetchall()
        )

    async def get(self, plate: str) -> RegistredVehicle:
        async with self._connection() as connection:
            cursor = await connection.cursor()
            regitred_vehicle = await self._get_registred_vehicle(plate, cursor)
            await regitred_vehicle.maintenance_performed(await self._fetch_service_items(plate, cursor))
        return regitred_vehicle

    async def _translate_vehicle_to_sql(self, vehicle: Vehicle) -> str:
        return f"""
            INSERT INTO vehicles(id,manufacturer,model,year)
                VALUES('{vehicle.id}', '{vehicle.manufacturer}', '{vehicle.model}', '{vehicle.year}')
                ON CONFLICT(id) DO UPDATE SET
                    manufacturer=excluded.manufacturer,
                    model=excluded.model,
                    year=excluded.year
        """

    async def _translate_registred_vehicle_to_sql(self, registred_vehicle: RegistredVehicle) -> str:
        return f"""
            INSERT INTO registred_vehicles(plate,vehicle_id)
                VALUES('{registred_vehicle.plate}', '{registred_vehicle.vehicle.id}')
                ON CONFLICT(plate) DO UPDATE SET
                    vehicle_id=excluded.vehicle_id
        """

    async def _translate_services_items_to_sql(self, services_items: Iterable[ServiceItem], plate: str) -> str:
        sql_insert = (
            "INSERT INTO services_items(service,kilometrage,months_since_vehicle_release,service_date,vehicle_plate) "
            "VALUES"
        )
        for service_item in services_items:
            sql_insert += (
                f"('{service_item.service}', {service_item.kilometrage}, {service_item.months_since_vehicle_release}, "
                f"'{service_item.service_date.isoformat()}', '{plate}'),"
            )
        sql_insert = sql_insert[:-1]  # Remove the last comma
        sql_insert += (
            "ON CONFLICT (service, kilometrage, months_since_vehicle_release, service_date, vehicle_plate) DO NOTHING"
        )
        return sql_insert

    async def add(self, registred_vehicle: RegistredVehicle):
        async with self._connection() as connection:
            cursor = await connection.cursor()
            await cursor.execute(await self._translate_vehicle_to_sql(registred_vehicle.vehicle))
            await cursor.execute(await self._translate_registred_vehicle_to_sql(registred_vehicle))
            services_history = await registred_vehicle.services_history()
            if services_history:
                await cursor.execute(
                    await self._translate_services_items_to_sql(services_history, registred_vehicle.plate)
                )


class EmptyCatalogConstraint(Exception):
    pass


class MaintenanceCatalogRepository(SQLiteRepository):
    async def _fetch_maintenance_items(self, vehicle_id: str):
        query = """
            SELECT kilometrage, month_interval, service AS "service [service]"
            FROM maintenance_items
            WHERE vehicle_id = :vehicle_id
        """
        async with self._connection() as connection:
            result = await connection.execute(query, {"vehicle_id": vehicle_id})
            return (
                MaintenanceItem(
                    service=row["service"],
                    kilometrage=row["kilometrage"],
                    month_interval=row["month_interval"],
                )
                for row in await result.fetchall()
            )

    async def get(self, vehicle_id: str) -> MaintenanceCatalog:
        maintenance_catalog = MaintenanceCatalog(vehicle_id)
        for maintenance_item in await self._fetch_maintenance_items(vehicle_id):
            await maintenance_catalog.add_maintenance_item(maintenance_item)
        return maintenance_catalog

    async def _translate_maintenance_items_to_sql(self, maintenance_catalog):
        sql_insert = "INSERT INTO maintenance_items(service, kilometrage, month_interval, vehicle_id) VALUES"
        for maintenance_item in maintenance_catalog:
            sql_insert += (
                f"('{maintenance_item.service}', {maintenance_item.kilometrage}, {maintenance_item.month_interval}, "
                f"'{maintenance_catalog.vehicle_id}'),"
            )
        sql_insert = sql_insert[:-1]  # Remove the last comma
        sql_insert += "ON CONFLICT (service, kilometrage, month_interval, vehicle_id) DO NOTHING"
        return sql_insert

    async def add(self, maintenance_catalog: MaintenanceCatalog):
        if not maintenance_catalog:
            raise EmptyCatalogConstraint
        async with self._connection() as connection:
            cursor = await connection.cursor()
            await cursor.execute(await self._translate_maintenance_items_to_sql(maintenance_catalog))
