from sqlite3 import Connection


def create_vehicle_table(connection: Connection):
    cur = connection.cursor()
    cur.execute("DROP TABLE IF EXISTS vehicles;")
    cur.execute(
        """
        CREATE TABLE vehicles (
            id VARCHAR(255) PRIMARY KEY,
            manufacturer VARCHAR(255) NOT NULL,
            model VARCHAR(255) NOT NULL,
            year VARCHAR(255) NOT NULL
        );
    """
    )


def create_registred_vehicles_table(connection: Connection):
    cur = connection.cursor()
    cur.execute("DROP TABLE IF EXISTS registred_vehicles;")
    cur.execute(
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


def create_maintenance_items_table(connection: Connection):
    cur = connection.cursor()
    cur.execute("DROP TABLE IF EXISTS maintenance_items;")
    cur.execute(
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
