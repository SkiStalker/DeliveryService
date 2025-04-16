from fastapi import APIRouter, Query
from pydantic import UUID4
from api.v1.models.delivery_models import (
    CreateDeliveryModel,
    DeliveryModel,
    SearchDeliveryModel,
    UpdateDeliveryModel,
)
from api.v1.routes.account_route import check_permission
from lib.http_tools import make_http_error
from grpc_build.delivery_service_pb2 import (
    GetDeliveryResponse,
    GetDeliveryRequest,
    CreateDeliveryRequest,
    CreateDeliveryResponse,
    UpdateDeliveryRequest,
    UpdateDeliveryResponse,
    SearchDeliveriesRequest,
    SearchDeliveriesResponse,
)

from api.v1.routes.responses.delivery_responses import (
    get_delivery_responses,
    create_delivery_responses,
    update_delivery_responses,
    search_deliveries_responses,
)
from grpc_build.delivery_service_pb2_grpc import DeliveryServiceStub
from context import app


router = APIRouter(prefix="/api/v1/delivery", tags=["delivery"])


@router.get(
    "/search",
    response_model=list[DeliveryModel],
    dependencies=[check_permission("READ_DELIVERY")],
    response_model_exclude_unset=True,
    responses=search_deliveries_responses,
)
async def search_deliveries(
    page: int = Query(...),
    sender_id: UUID4 | None = Query(None),
    receiver_id: UUID4 | None = Query(None),
):
    delivery_stub: DeliveryServiceStub = app.state.delivery_stub
    resp: SearchDeliveriesResponse = delivery_stub.SearchDeliveries(
        SearchDeliveriesRequest(
            page=page,
            searching_delivery_data=SearchDeliveryModel(
                sender_id=sender_id, receiver_id=receiver_id
            ).to_SearchDeliveryData(),
        )
    )

    if resp.code == 200:
        return [
            DeliveryModel.from_grpc_message(delivery)
            for delivery in resp.deliveries.arr
        ]
    else:
        make_http_error(resp)


@router.get(
    "/{delivery_id}",
    response_model=DeliveryModel,
    dependencies=[check_permission("READ_DELIVERY")],
    response_model_exclude_unset=True,
    responses=get_delivery_responses
)
async def get_delivery(delivery_id: UUID4):
    delivery_stub: DeliveryServiceStub = app.state.delivery_stub
    resp: GetDeliveryResponse = delivery_stub.GetDelivery(
        GetDeliveryRequest(delivery_id=str(delivery_id))
    )
    if resp.code == 200:
        return DeliveryModel.from_grpc_message(resp.delivery_data)
    else:
        make_http_error(resp)


@router.post(
    "/",
    response_model=DeliveryModel,
    dependencies=[check_permission("CREATE_DELIVERY")],
    response_model_exclude_unset=True,
    responses=create_delivery_responses
)
async def create_delivery(creating_delivery: CreateDeliveryModel):
    delivery_stub: DeliveryServiceStub = app.state.delivery_stub
    resp: CreateDeliveryResponse = delivery_stub.CreateDelivery(
        CreateDeliveryRequest(
            creating_delivery_data=creating_delivery.to_CreateDeliveryData()
        )
    )
    if resp.code == 200:
        return DeliveryModel.from_grpc_message(resp.delivery_data)
    else:
        make_http_error(resp)


@router.put(
    "/{delivery_id}",
    response_model=DeliveryModel,
    dependencies=[check_permission("UPDATE_DELIVERY")],
    response_model_exclude_unset=True,
    responses=update_delivery_responses
)
async def update_delivery(delivery_id: UUID4, updating_delivery: UpdateDeliveryModel):
    delivery_stub: DeliveryServiceStub = app.state.delivery_stub
    resp: UpdateDeliveryResponse = delivery_stub.UpdateDelivery(
        UpdateDeliveryRequest(
            delivery_id=str(delivery_id), updating_delivery_data=updating_delivery
        )
    )
    if resp.code == 200:
        return DeliveryModel.from_grpc_message(resp.delivery_data)
    else:
        make_http_error(resp)
