import asyncio

from aiosqlite import Connection

from src.database.connection import db_connection


async def create_vehicle_table(connection: Connection):
    cur = await connection.cursor()
    await cur.execute(
        """
        CREATE TABLE IF NOT EXISTS vehicles (
            id VARCHAR(255) PRIMARY KEY,
            manufacturer VARCHAR(255) NOT NULL,
            model VARCHAR(255) NOT NULL,
            year INT NOT NULL
        );
    """
    )


async def create_registred_vehicles_table(connection: Connection):
    cur = await connection.cursor()
    await cur.execute(
        """
        CREATE TABLE IF NOT EXISTS registred_vehicles (
            plate VARCHAR(255) PRIMARY KEY,
            vehicle_id VARCHAR(255) NOT NULL,
            CONSTRAINT fk_vehicle
                FOREIGN KEY(vehicle_id)
                    REFERENCES vehicles(id)
        );
    """
    )


async def create_maintenance_items_table(connection: Connection):
    cur = await connection.cursor()
    await cur.execute(
        """
        CREATE TABLE IF NOT EXISTS maintenance_items (
            service VARCHAR(255) NOT NULL,
            kilometrage INT,
            month_interval INT,
            vehicle_id VARCHAR(255) NOT NULL,
            CONSTRAINT fk_vehicle
                FOREIGN KEY(vehicle_id)
                    REFERENCES vehicles(id)
                CHECK (kilometrage IS NOT NULL OR month_interval IS NOT NULL)
                UNIQUE (service, kilometrage, month_interval, vehicle_id)
        );
    """
    )


async def create_services_items_table(connection: Connection):
    cur = await connection.cursor()
    await cur.execute(
        """
        CREATE TABLE IF NOT EXISTS services_items (
            service VARCHAR(255) NOT NULL,
            kilometrage INT NOT NULL,
            months_since_vehicle_release INT NOT NULL,
            service_date VARCHAR(255) NOT NULL,
            vehicle_plate VARCHAR(255) NOT NULL,
            CONSTRAINT fk_vehicle_plate
                FOREIGN KEY(vehicle_plate)
                    REFERENCES registred_vehicles(plate)
                UNIQUE (service, kilometrage, months_since_vehicle_release, service_date, vehicle_plate)
        );
    """
    )


async def tables():
    async with db_connection() as connection:
        await create_vehicle_table(connection)
        await create_registred_vehicles_table(connection)
        await create_maintenance_items_table(connection)
        await create_services_items_table(connection)


if __name__ == "__main__":
    asyncio.run(tables())
