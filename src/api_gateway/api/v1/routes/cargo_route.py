from fastapi import APIRouter, Query
from pydantic import UUID4

from api.v1.models.cargo_models import CargoModel, CreateCargoModel, UpdateCargoModel
from api.v1.routes.account_route import check_permission
from grpc_build.cargo_service_pb2 import (
    CreateCargoRequest,
    CreateCargoResponse,
    GetCargoRequest,
    GetCargoResponse,
    GetUserCargosRequest,
    GetUserCargosResponse,
    UpdateCargoRequest,
    UpdateCargoResponse,
)

from grpc_build.cargo_service_pb2_grpc import CargoServiceStub
from lib.http_tools import make_http_error
from context import app

from api.v1.routes.responses.cargo_responses import get_cargo_responses, create_cargo_responses, update_cargo_responses, get_user_cargos_responses


router = APIRouter(prefix="/api/v1/cargo", tags=["cargo"])


@router.post(
    "/",
    response_model=CargoModel,
    dependencies=[check_permission("CREATE_CARGO")],
    response_model_exclude_unset=True,
    responses=create_cargo_responses
)
async def create_cargo(cargo: CreateCargoModel):
    cargo_stub: CargoServiceStub = app.state.cargo_stub
    resp: CreateCargoResponse = await cargo_stub.CreateCargo(
        CreateCargoRequest(creating_cargo_data=cargo.to_CreateCargoData())
    )

    if resp.code == 201:
        return CargoModel.from_grpc_message(resp.cargo_data)
    else:
        make_http_error(resp)


@router.get(
    "/{cargo_id}",
    response_model=CargoModel,
    dependencies=[check_permission("READ_CARGO")],
    responses=get_cargo_responses
)
async def get_cargo(cargo_id: UUID4):
    cargo_stub: CargoServiceStub = app.state.cargo_stub
    resp: GetCargoResponse = cargo_stub.GetCargo(GetCargoRequest(cargo_id=cargo_id))
    if resp.code == 200:
        return CargoModel.from_grpc_message(resp.cargo_data)
    else:
        make_http_error(resp)


@router.get(
    "/user_cargos",
    response_model=list[CargoModel],
    dependencies=[check_permission("READ_CARGO")],
    responses=get_user_cargos_responses
)
async def get_user_cargos(page: int = Query(...), user_id: UUID4 = Query(...)):
    cargo_stub: CargoServiceStub = app.state.cargo_stub
    resp: GetUserCargosResponse = cargo_stub.GetUserCargos(
        GetUserCargosRequest(page=page, user_id=str(user_id))
    )
    if resp.code == 200:
        return [CargoModel.from_grpc_message(cargo_data) for cargo_data in resp.arr]
    else:
        make_http_error(resp)


@router.put(
    "/{cargo_id}",
    response_model=CargoModel,
    dependencies=[check_permission("UPDATE_CARGO")],
    responses=update_cargo_responses
)
async def update_cargo(cargo_id: UUID4, updating_cargo: UpdateCargoModel):
    cargo_stub: CargoServiceStub = app.state.cargo_stub

    resp: UpdateCargoResponse = cargo_stub.UpdateCargo(
        UpdateCargoRequest(
            cargo_id=cargo_id, updating_cargo_data=updating_cargo.to_UpdateCargoData()
        )
    )

    if resp.code == 200:
        return CargoModel.from_grpc_message(resp.cargo_data)
    else:
        make_http_error(resp)
