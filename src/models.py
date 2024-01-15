from collections import defaultdict
from collections.abc import Iterable, Iterator
from datetime import datetime, timezone
from enum import StrEnum
from operator import attrgetter


class Service(StrEnum):
    ENGINE_OIL_REPLACEMENT = "engine_oil_replacement"
    ENGINE_OIL_FILTER_REPLACEMENT = "engine_oil_filter_replacement"
    AIR_FILTER_REPLACEMENT = "air_filter_replacement"
    INSPECT_VALVE_CLEARANCE = "inspect_valve_clearance"
    FUEL_FILTER_REPLACEMENT = "fuel_filter_replacement"
    SPARK_PLUGS_REPLACEMENT = "spark_plugs_replacement"
    INSPECT_ACCESSORY_DRIVE_BELT = "inspect_accessory_drive_belt"
    INSPECT_IDLE_SPEED = "inspect_idle_speed"
    ENGINE_COOLANT_REPLACEMENT = "engine_coolant_replacement"
    INSPECT_BATTERY_CHARGE_CAPACITY = "inspect_battery_charge_capacity"
    TRANSMISSION_FLUID_REPLACEMENT = "transmission_fluid_replacement"
    INSPECT_BRAKES = "inspect_brakes"
    BRAKE_FLUID_REPLACEMENT = "brake_fluid_replacement"
    INSPECT_PARKING_BRAKE = "inspect_parking_brake"
    INSPECT_DUST_AND_POLLEN_FILTER_REPLACEMENT = "dust_and_pollen_filter_replacement"
    TIRES_ROTATION = "tires_rotation"
    INSPECT_STEERING_TERMINALS_AND_BOX_AND_HOODS = "inspect_steering_terminals_and_box_and_hoods"
    INSPECT_SUSPENSION_COMPONENTS = "inspect_suspension_components"
    INSPECT_DRIVE_SHAFT_BOOTS = "inspect_drive_shaft_boots"
    INSPECT_BRAKE_HOSES_AND_LINES = "inspect_inspect_brake_hoses_and_lines"
    INSPECT_FUEL_PIPES_AND_CONNECTIONS = "inspect_inspect_fuel_pipes_and_connections"


class MaintenanceItem:
    def __init__(self, service: Service, kilometrage: int, month_interval: int):
        self.service = service
        self.kilometrage = kilometrage
        self.month_interval = month_interval

    def __eq__(self, other):
        return vars(self) == vars(other)


class MaintenanceCatalog:
    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        self._maintenance_items = {}

    async def add_maintenance_item(self, maintenance_item: MaintenanceItem):
        self._maintenance_items[maintenance_item.service] = maintenance_item

    def __iter__(self) -> Iterator[MaintenanceItem]:
        return iter(self._maintenance_items.values())


class Vehicle:
    def __init__(self, manufacturer: str, model: str, year: int):
        self._id = ""
        self.manufacturer = manufacturer
        self.model = model
        self.year = year

    @property
    def id(self) -> str:
        if not self._id:
            self._id = f"{self.manufacturer} {self.model} {self.year}"
        return self._id


class NextServiceItem:
    def __init__(self, service: Service, kilometrage: int, months_since_vehicle_release: int):
        self.service = service
        self.kilometrage = kilometrage
        self.months_since_vehicle_release = months_since_vehicle_release

    def __eq__(self, other):
        return vars(self) == vars(other)


class ServiceItem:
    def __init__(
        self,
        service: Service,
        kilometrage: int,
        months_since_vehicle_release: int,
        service_date: datetime = None,
    ):
        self.service = service
        self.kilometrage = kilometrage
        self.months_since_vehicle_release = months_since_vehicle_release
        self.service_date = service_date or datetime.now(tz=timezone.utc)

    def __eq__(self, other):
        return vars(self) == vars(other)


class ServicesPerItem:
    def __init__(self):
        self._items: list[ServiceItem] = []

    def __len__(self):
        return len(self._items)

    def __iter__(self) -> Iterator[ServiceItem]:
        return iter(self._items)

    async def add(self, service_item: ServiceItem):
        self._items.append(service_item)

    async def _last_service(self) -> ServiceItem:
        return sorted(self._items, key=attrgetter("service_date"), reverse=True)[0]

    async def next_service(self, maintenance_item: MaintenanceItem) -> NextServiceItem:
        last_service = await self._last_service()
        return NextServiceItem(
            service=last_service.service,
            kilometrage=last_service.kilometrage + maintenance_item.kilometrage,
            months_since_vehicle_release=last_service.months_since_vehicle_release + maintenance_item.month_interval,
        )


class NextMaintenance:
    def __init__(self):
        self._items: list[NextServiceItem] = []

    def __getitem__(self, index):
        return self._items[index]

    def __len__(self):
        return len(self._items)

    async def add(self, next_service_item: NextServiceItem):
        self._items.append(next_service_item)


class RegistredVehicle:
    def __init__(self, plate: str, vehicle: Vehicle):
        self.plate = plate
        self.vehicle = vehicle
        self._services = defaultdict(ServicesPerItem)

    async def services_history(self):
        return [service_item for services_per_item in self._services.values() for service_item in services_per_item]

    async def maintenance_performed(self, services: Iterable[ServiceItem]):
        for item_service in services:
            services_per_item = self._services[item_service.service]
            await services_per_item.add(item_service)

    async def _get_next_service_item(self, maintenance_item):
        services_per_item = self._services.get(maintenance_item.service)
        if services_per_item:
            return await services_per_item.next_service(maintenance_item)
        return NextServiceItem(
            service=maintenance_item.service,
            kilometrage=maintenance_item.kilometrage,
            months_since_vehicle_release=maintenance_item.month_interval,
        )

    async def next_maintenance(self, maintenance_catalog: MaintenanceCatalog) -> NextMaintenance:
        next_maintenace = NextMaintenance()
        for maintenance_item in maintenance_catalog:
            await next_maintenace.add(await self._get_next_service_item(maintenance_item))
        return next_maintenace
