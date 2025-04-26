import asyncio
import os
import grpc
from grpc import ServicerContext

from grpc_build.cargo_service_pb2_grpc import (
    CargoServiceServicer,
    add_CargoServiceServicer_to_server,
)
from repositories.cargo_repository import CargoRepository
from grpc_build.cargo_service_pb2 import (
    CargoDataArray,
    CreateCargoRequest,
    CreateCargoResponse,
    GetCargoRequest,
    GetCargoResponse,
    GetUserCargosRequest,
    GetUserCargosResponse,
    UpdateCargoRequest,
    UpdateCargoResponse,
)
from models.cargo_models import CreateCargoModel, UpdateCargoModel


class CargoService(CargoServiceServicer):
    def __init__(self, cargo_rep: CargoRepository):
        self._cargo_rep = cargo_rep

    async def CreateCargo(
        self, request: CreateCargoRequest, context: ServicerContext
    ) -> CreateCargoResponse:
        try:
            creating_cargo_model = CreateCargoModel.from_grpc_message(
                request.creating_cargo_data
            )

            created_cargo_model = await self._cargo_rep.create_cargo(
                creating_cargo_model
            )

            if created_cargo_model is not None:
                return CreateCargoResponse(
                    code=200, cargo_data=created_cargo_model.to_CargoData()
                )
            else:
                return CreateCargoResponse(code=400, message="Can not create cargo")

        except Exception as ex:
            return CreateCargoResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )

    async def UpdateCargo(
        self, request: UpdateCargoRequest, context: ServicerContext
    ) -> UpdateCargoResponse:
        try:
            cargo_id = request.cargo_id
            updating_cargo_model = UpdateCargoModel.from_grpc_message(
                request.updating_cargo_data
            )
            if updating_cargo_model is None:
                updated_cargo_model = await self._cargo_rep.update_cargo(
                    cargo_id, updating_cargo_model
                )

                if updated_cargo_model is not None:
                    return UpdateCargoResponse(
                        code=200, cargo_data=updated_cargo_model.to_CargoData()
                    )
                else:
                    return UpdateCargoResponse(code=404, message="Cargo not found")

            else:
                not_updated_cargo_model = await self._cargo_rep.get_cargo_by_id(
                    cargo_id
                )

                if not_updated_cargo_model is not None:
                    return UpdateCargoResponse(
                        code=200, cargo_data=not_updated_cargo_model.to_CargoData()
                    )
                else:
                    return UpdateCargoResponse(code=404, message="Cargo not found")
        except Exception as ex:
            return UpdateCargoResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )

    async def GetCargo(
        self, request: GetCargoRequest, context: ServicerContext
    ) -> GetCargoResponse:
        try:
            cargo_id = request.cargo_id

            cargo_model = await self._cargo_rep.get_cargo_by_id(cargo_id)

            if cargo_model is not None:
                return GetCargoResponse(code=200, cargo_data=cargo_model.to_CargoData())
            else:
                return GetCargoResponse(code=404, message="Cargo not found")

        except Exception as ex:
            return GetCargoResponse(code=500, message=f"Error : {ex}, args : {ex.args}")

    async def GetUserCargos(
        self, request: GetUserCargosRequest, context: ServicerContext
    ) -> GetUserCargosResponse:
        try:
            user_id = request.user_id
            page = request.page

            cargo_models = await self._cargo_rep.get_user_cargos(user_id, page)

            return GetUserCargosResponse(
                code=200,
                arr=CargoDataArray(
                    cargo_data=[
                        cargo_model.to_CargoData() for cargo_model in cargo_models
                    ]
                ),
            )

        except Exception as ex:
            return GetUserCargosResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )


async def serve():

    server = grpc.aio.server()

    async with CargoRepository() as cargo_rep:
        add_CargoServiceServicer_to_server(CargoService(cargo_rep), server)
        server.add_insecure_port(f"[::]:{os.environ.get("CARGO_SERVICE_PORT", 50053)}")
        print(
            f"Async gRPC Server started at port {os.environ.get("CARGO_SERVICE_PORT", 50053)}"
        )
        await server.start()
        try:
            await server.wait_for_termination()
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(serve())
