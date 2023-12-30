from collections import defaultdict
from collections.abc import Sequence, Iterator
from datetime import datetime, timezone
from enum import StrEnum
from operator import attrgetter


class Service(StrEnum):
    ENGINE_OIL_REPLACEMENT = "engine_oil_replacement"
    ENGINE_OIL_FILTER_REPLACEMENT = "engine_oil_filter_replacement"


class MaintenanceItem:
    def __init__(self, service: Service, kilometrage: int, month_interval: int):
        self.service = service
        self.kilometrage = kilometrage
        self.month_interval = month_interval


class MaintenanceCatalog:
    def __init__(self):
        self._maintenance_items = {}

    def add(self, maintenance_item: MaintenanceItem):
        self._maintenance_items[maintenance_item.service] = maintenance_item

    def __iter__(self) -> Iterator[MaintenanceItem]:
        return iter(self._maintenance_items.values())


class Vehicle:
    def __init__(self, manufacturer: str, model: str, year: int, maintenance_catalog: MaintenanceCatalog):
        self.manufacturer = manufacturer
        self.model = model
        self.year = year
        self.maintenance_catalog = maintenance_catalog


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

    def add(self, service_item: ServiceItem):
        self._items.append(service_item)

    def _last_service(self) -> ServiceItem:
        return sorted(self._items, key=attrgetter("service_date"), reverse=True)[0]

    def next_service(self, maintenance_item: MaintenanceItem) -> NextServiceItem:
        last_service = self._last_service()
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

    def add(self, next_service_item: NextServiceItem):
        self._items.append(next_service_item)


class RegistredVehicle:
    def __init__(self, plate: str, vehicle: Vehicle):
        self.plate = plate
        self.vehicle = vehicle
        self._services = defaultdict(ServicesPerItem)

    def maintenance_performed(self, services: Sequence[ServiceItem]):
        for item_service in services:
            services_per_item = self._services[item_service.service]
            services_per_item.add(item_service)

    def _get_next_service_item(self, maintenance_item):
        services_per_item = self._services.get(maintenance_item.service)
        if services_per_item:
            return services_per_item.next_service(maintenance_item)
        return NextServiceItem(
            service=maintenance_item.service,
            kilometrage=maintenance_item.kilometrage,
            months_since_vehicle_release=maintenance_item.month_interval,
        )

    def next_maintenance(self) -> NextMaintenance:
        next_maintenace = NextMaintenance()
        for maintenance_item in self.vehicle.maintenance_catalog:
            next_maintenace.add(self._get_next_service_item(maintenance_item))
        return next_maintenace
