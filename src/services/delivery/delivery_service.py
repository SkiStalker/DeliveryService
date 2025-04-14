import asyncio
import os
import grpc
from grpc import ServicerContext

from repositories.delivery_repository import DeliveryRepository

from grpc_build.delivery_service_pb2_grpc import (
    DeliveryServiceServicer,
    add_DeliveryServiceServicer_to_server,
)
from grpc_build.delivery_service_pb2 import (
    CreateDeliveryRequest,
    CreateDeliveryResponse,
    DeliveryDataArray,
    GetDeliveryRequest,
    GetDeliveryResponse,
    SearchDeliveriesRequest,
    SearchDeliveriesResponse,
    UpdateDeliveryRequest,
    UpdateDeliveryResponse,
)
from models.delivery_models import CreateDeliveryModel, SearchDeliveryModel, UpdateDeliveryModel


class DeliveryService(DeliveryServiceServicer):
    def __init__(self, delivery_rep: DeliveryRepository):
        self._delivery_rep = delivery_rep

    async def CreateDelivery(
        self, request: CreateDeliveryRequest, context: ServicerContext
    ) -> CreateDeliveryResponse:
        try:
            creating_model = CreateDeliveryModel.from_grpc_message(
                request.creating_delivery_data
            )
            created_model = await self._delivery_rep.create_delivery(creating_model)
            if creating_model is not None:
                return CreateDeliveryResponse(
                    code=201, delivery_data=created_model.to_DeliveryData()
                )
            else:
                return CreateDeliveryResponse(code=400, message="Can't create delivery")

        except Exception as ex:
            return CreateDeliveryResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )

    async def UpdateDelivery(
        self, request: UpdateDeliveryRequest, context: ServicerContext
    ) -> UpdateDeliveryResponse:
        try:
            delivery_id = request.delivery_id
            updating_model = UpdateDeliveryModel.from_grpc_message(
                request.updating_delivery_data
            )

            if updating_model is not None:
                updated_model = await self._delivery_rep.update_delivery(
                    delivery_id, updating_model
                )
            else:
                updated_model = await self._delivery_rep.get_delivery_by_id(delivery_id)

            if updated_model is not None:
                return UpdateDeliveryResponse(code=200, delivery_data=updated_model)
            else:
                return UpdateDeliveryResponse(code=404, message="Delivery not found")

        except Exception as ex:
            return UpdateDeliveryResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )

    async def SearchDeliveries(
        self,
        request: SearchDeliveriesRequest,
        context: ServicerContext,
    ) -> SearchDeliveriesResponse:
        try:
            page = request.page

            search_model = SearchDeliveryModel.from_grpc_message(request.searching_delivery_data)
            
            deliveries = await self._delivery_rep.search_deliveries(page, search_model)

            return SearchDeliveriesResponse(
                code=200,
                deliveries=DeliveryDataArray(
                    arr=[delivery.to_DeliveryData() for delivery in deliveries]
                ),
            )

        except Exception as ex:
            return SearchDeliveriesResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )

    async def GetDelivery(
        self, request: GetDeliveryRequest, context: ServicerContext
    ) -> GetDeliveryResponse:
        try:
            delivery_id = request.delivery_id

            delivery_model = await self._delivery_rep.get_delivery_by_id(delivery_id)

            if delivery_model is not None:
                return GetDeliveryResponse(
                    code=200, delivery_data=delivery_model.to_DeliveryData()
                )
            else:
                return GetDeliveryResponse(code=404, message="Delivery not found")

        except Exception as ex:
            return GetDeliveryResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )


async def serve():

    server = grpc.aio.server()

    delivery_rep = DeliveryRepository()

    await delivery_rep.connect()

    add_DeliveryServiceServicer_to_server(DeliveryService(delivery_rep), server)
    server.add_insecure_port(f"[::]:{os.environ.get("DELIVERY_SERVICE_PORT", 50054)}")
    print(
        f"Async gRPC Server started at port {os.environ.get("DELIVERY_SERVICE_PORT", 50054)}"
    )
    await server.start()
    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        pass

    await delivery_rep.disconnect()


if __name__ == "__main__":
    asyncio.run(serve())
