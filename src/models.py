from collections import defaultdict
from collections.abc import Sequence
from datetime import datetime, timezone
from enum import StrEnum
from operator import attrgetter


class Service(StrEnum):
    MOTOR_OIL_REPLACEMENT = "motor_oil_replacement"


class ItemMaintenance:
    def __init__(self, service: Service, kilometrage: int, month_interval: int):
        self.service = service
        self.kilometrage = kilometrage
        self.month_interval = month_interval


class MaintenanceCatalog:
    def __init__(self):
        self._maintenance_items = {}

    def add(self, item_maintenance: ItemMaintenance):
        self._maintenance_items[item_maintenance.service] = item_maintenance

    def __getitem__(self, service: Service) -> ItemMaintenance:
        return self._maintenance_items[service]


class Vehicle:
    def __init__(self, manufacturer: str, model: str, year: int, maintenance_catalog: MaintenanceCatalog):
        self.manufacturer = manufacturer
        self.model = model
        self.year = year
        self.maintenance_catalog = maintenance_catalog


class NextItemService:
    def __init__(self, service: Service, kilometrage: int, months_since_vehicle_release: int):
        self.service = service
        self.kilometrage = kilometrage
        self.months_since_vehicle_release = months_since_vehicle_release

    def __eq__(self, other):
        return vars(self) == vars(other)


class ItemService:
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
        self._items: list[ItemService] = []

    def __len__(self):
        return len(self._items)

    def add(self, item_service: ItemService):
        self._items.append(item_service)

    def _last_service(self) -> ItemService:
        return sorted(self._items, key=attrgetter("service_date"), reverse=True)[0]

    def next_maintenance(self, maintenance_catalog: MaintenanceCatalog) -> NextItemService:
        last_service = self._last_service()
        item_maintenace = maintenance_catalog[last_service.service]
        return NextItemService(
            service=last_service.service,
            kilometrage=last_service.kilometrage + item_maintenace.kilometrage,
            months_since_vehicle_release=last_service.months_since_vehicle_release + item_maintenace.month_interval,
        )


class NextMaintenance:
    def __init__(self):
        self._items: list[NextItemService] = []

    def __getitem__(self, index):
        return self._items[index]

    def add(self, item_service: NextItemService):
        self._items.append(item_service)


class VehicleRegistration:
    def __init__(self, plate: str, vehicle: Vehicle):
        self.plate = plate
        self.vehicle = vehicle
        self._services = defaultdict(ServicesPerItem)

    def maintenance_performed(self, services: Sequence[ItemService]):
        for item_service in services:
            services_per_item = self._services[item_service.service]
            services_per_item.add(item_service)

    def next_maintenance(self) -> NextMaintenance:
        next_maintenace = NextMaintenance()
        for service_per_item in self._services.values():
            next_maintenace.add(service_per_item.next_maintenance(maintenance_catalog=self.vehicle.maintenance_catalog))
        return next_maintenace
