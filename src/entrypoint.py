import pydantic
from inspect import signature
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.models import ServiceItem
from src.repositories import RegistredVehicleRepository, MaintenanceCatalogRepository
from src.services import calculate_next_maintenace

app = FastAPI()


def as_payload(cls, extra_fields={}):
    return pydantic.create_model(
        f"{cls.__init__}Payload",
        **{
            key: (value.annotation, ...)
            for key, value in signature(cls.__init__).parameters.items()
            if not key == "self"
        },
        **extra_fields,
    )


@app.post("/registred-vehicles/{plate}/services-items")
async def add_service_item(service_item_payload: as_payload(ServiceItem, extra_fields={"plate": (str, ...)})):
    repository = RegistredVehicleRepository()
    registred_vehicle = await repository.get(plate=service_item_payload.plate)
    await registred_vehicle.maintenance_performed([ServiceItem(**service_item_payload.model_dump(exclude={"plate"}))])
    await repository.add(registred_vehicle)
    return JSONResponse(content={}, status_code=201)


@app.get("/registred-vehicles/{plate}/next-maintenance")
async def next_maintenance(plate: str):
    next_maintenace = await calculate_next_maintenace(
        plate,
        RegistredVehicleRepository(),
        MaintenanceCatalogRepository(),
    )
    result = [
        {
            "service": next_service_item.service,
            "kilometrage": next_service_item.kilometrage,
            "months_since_vehicle_release": next_service_item.months_since_vehicle_release,
        }
        for next_service_item in next_maintenace
    ]
    return JSONResponse(content=result, status_code=200)
