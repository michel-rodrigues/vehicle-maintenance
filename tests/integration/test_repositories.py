import aiosqlite
import sqlite3
from datetime import datetime

from src.models import Service, MaintenanceItem
from src.repositories import RegistredVehicleRepository, MaintenanceCatalogRepository


async def test_get_registred_vehicle():
    con = await aiosqlite.connect(":memory:", detect_types=sqlite3.PARSE_COLNAMES)
    cur = await con.cursor()
    await cur.execute("DROP TABLE IF EXISTS vehicles;")
    await cur.execute(
        """
        CREATE TABLE vehicles (
            id VARCHAR(255) PRIMARY KEY,
            manufacturer VARCHAR(255) NOT NULL,
            model VARCHAR(255) NOT NULL,
            year VARCHAR(255) NOT NULL
        );
    """
    )
    await cur.execute(
        """
        INSERT INTO vehicles VALUES
            ('Honda Fit 2015', 'Honda', 'Fit', '2015')
    """
    )

    await cur.execute("DROP TABLE IF EXISTS registred_vehicles;")
    await cur.execute(
        """
        CREATE TABLE registred_vehicles (
            plate VARCHAR(255) PRIMARY KEY,
            vehicle_id VARCHAR(255) NOT NULL,
            CONSTRAINT fk_vehicle
                FOREIGN KEY(vehicle_id)
                    REFERENCES vehicles(id)
        );
    """
    )
    await cur.execute(
        """
        INSERT INTO registred_vehicles VALUES
            ('ABC1A10', 'Honda Fit 2015')
    """
    )

    await cur.execute("DROP TABLE IF EXISTS services_items;")
    await cur.execute(
        """
        CREATE TABLE services_items (
            service VARCHAR(255) NOT NULL,
            kilometrage INT NOT NULL,
            months_since_vehicle_release INT NOT NULL,
            service_date VARCHAR(255) NOT NULL,
            vehicle_plate VARCHAR(255) NOT NULL,
            CONSTRAINT fk_vehicle_plate
                FOREIGN KEY(vehicle_plate)
                    REFERENCES registred_vehicles(plate)
        );
    """
    )
    await cur.execute(
        """
        INSERT INTO services_items VALUES
            ('engine_oil_replacement', 10000, 10, '2024-01-02T02:55:10.369639+00:00', 'ABC1A10'),
            ('engine_oil_replacement', 20000, 18, '2024-08-23T02:55:10.369639+00:00', 'ABC1A10'),
            ('engine_oil_filter_replacement', 10000, 10, '2024-01-02T02:55:10.369639+00:00', 'ABC1A10')
    """
    )

    await con.commit()

    registred_vehicle = await RegistredVehicleRepository(con).get(plate="ABC1A10")
    assert registred_vehicle.plate == "ABC1A10"
    assert registred_vehicle.vehicle.manufacturer == "Honda"
    assert registred_vehicle.vehicle.model == "Fit"
    assert registred_vehicle.vehicle.year == "2015"
    services = registred_vehicle._services
    assert len(services) == 2
    assert len(services[Service.ENGINE_OIL_REPLACEMENT]) == 2
    assert len(services[Service.ENGINE_OIL_FILTER_REPLACEMENT]) == 1
    service_per_item = services[Service.ENGINE_OIL_REPLACEMENT]._items[0]
    assert service_per_item.service_date == datetime.fromisoformat("2024-01-02T02:55:10.369639+00:00")


async def test_get_maintenance_catalog():
    con = await aiosqlite.connect(":memory:", detect_types=sqlite3.PARSE_COLNAMES)
    cur = await con.cursor()
    await cur.execute("DROP TABLE IF EXISTS maintenance_items;")
    await cur.execute(
        """
        CREATE TABLE maintenance_items (
            service VARCHAR(255) NOT NULL,
            kilometrage INT,
            month_interval INT,
            vehicle_id VARCHAR(255) NOT NULL,
            CONSTRAINT fk_vehicle
                FOREIGN KEY(vehicle_id)
                    REFERENCES vehicles(id)
                CHECK (kilometrage IS NOT NULL OR month_interval IS NOT NULL)
        );
    """
    )
    await cur.execute(
        """
        INSERT INTO maintenance_items VALUES
            ('engine_oil_replacement', '10000', '12', 'Honda Fit 2015'),
            ('engine_oil_filter_replacement', '10000', '12', 'Honda Fit 2015')
    """
    )
    await con.commit()

    expected_maintenance_items = [
        MaintenanceItem(
            service=Service.ENGINE_OIL_REPLACEMENT,
            kilometrage=10_000,
            month_interval=12,
        ),
        MaintenanceItem(
            service=Service.ENGINE_OIL_FILTER_REPLACEMENT,
            kilometrage=10_000,
            month_interval=12,
        ),
    ]

    maintenance_catalog = await MaintenanceCatalogRepository(con).get(vehicle_id="Honda Fit 2015")
    assert list(maintenance_catalog) == expected_maintenance_items
