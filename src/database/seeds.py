from sqlite3 import Connection


def populate_vehicle_table(connection: Connection):
    cur = connection.cursor()
    cur.execute(
        """
        INSERT INTO vehicles VALUES
            ('Honda Fit 2015', 'Honda', 'Fit', '2015')
    """
    )


def populate_registred_vehicles_table(connection: Connection):
    cur = connection.cursor()
    cur.execute(
        """
        INSERT INTO registred_vehicles VALUES
            ('FZG5A15', 'Honda Fit 2015')
    """
    )


def populate_maintenance_items_table(connection: Connection):
    cur = connection.cursor()
    cur.execute(
        """
        INSERT INTO maintenance_items VALUES
            ('engine_oil_replacement', '10000', '12', 'Honda Fit 2015'),
            ('engine_oil_filter_replacement', '10000', '12', 'Honda Fit 2015'),
            ('air_filter_replacement', '20000', '', 'Honda Fit 2015'),
            ('inspect_valve_clearance', '40000', '', 'Honda Fit 2015'),
            ('fuel_filter_replacement', '10000', '', 'Honda Fit 2015'),
            ('spark_plugs_replacement', '60000', '', 'Honda Fit 2015'),
            ('inspect_accessory_drive_belt', '40000', '24', 'Honda Fit 2015'),
            ('inspect_idle_speed', '120000', '72', 'Honda Fit 2015'),
            ('engine_coolant_replacement', '100000', '60', 'Honda Fit 2015'),
            ('inspect_battery_charge_capacity', '', '12', 'Honda Fit 2015'),
            ('transmission_fluid_replacement', '40000', '24', 'Honda Fit 2015'),
            ('inspect_brakes', '10000', '6', 'Honda Fit 2015'),
            ('brake_fluid_replacement', '', '36', 'Honda Fit 2015'),
            ('inspect_parking_brake', '20000', '12', 'Honda Fit 2015'),
            ('dust_and_pollen_filter_replacement', '20000', '12', 'Honda Fit 2015'),
            ('tires_rotation', '10000', '', 'Honda Fit 2015'),
            ('inspect_steering_terminals_and_box_and_hoods', '10000', '12', 'Honda Fit 2015'),
            ('inspect_suspension_components', '10000', '12', 'Honda Fit 2015'),
            ('inspect_drive_shaft_boots', '10000', '12', 'Honda Fit 2015'),
            ('inspect_inspect_brake_hoses_and_lines', '20000', '12', 'Honda Fit 2015'),
            ('inspect_inspect_fuel_pipes_and_connections', '20000', '12', 'Honda Fit 2015')
    """
    )
