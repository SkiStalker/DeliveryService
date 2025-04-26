import json
from pydantic import UUID4
from api.v1.models.payment_models import PaymentInfoModel, PaymentRuleModel
from api.v1.routes.account_route import check_permission
from api.v1.models.item_models import ItemModel
from lib.http_tools import make_http_error
from grpc_build.payment_service_pb2 import (
    AcceptPaymentRequest,
    AcceptPaymentResponse,
    AddPaymentRuleRequest,
    AddPaymentRuleResponse,
    MakePaymentRequest,
    MakePaymentResponse,
    SearchPaymentsRequest,
    SearchPaymentsResponse,
)
from grpc_build.payment_service_pb2_grpc import PaymentServiceStub
from context import app
from fastapi import APIRouter, Body, Query, status

from api.v1.routes.responses.payment_responses import (
    make_payment_responses,
    accept_payment_responses,
    search_payments_responses,
    add_payment_rule_responses,
)

router = APIRouter(prefix="/api/v1/payment", tags=["payment"])


@router.get(
    "/",
    response_model=PaymentInfoModel,
    dependencies=[check_permission("MAKE_PAYMENT")],
    response_model_exclude_unset=True,
    responses=make_payment_responses,
)
async def make_payment(delivery_id: UUID4 = Query(...)):
    payment_stub: PaymentServiceStub = app.state.payment_stub
    resp: MakePaymentResponse = await payment_stub.MakePayment(
        MakePaymentRequest(delivery_id=str(delivery_id))
    )
    if resp.code == 200:
        return PaymentInfoModel.from_grpc_message(resp.payment_data)
    else:
        make_http_error(resp)


@router.post("/", responses=accept_payment_responses)
async def accept_payment(body=Body(...)):
    payment_stub: PaymentServiceStub = app.state.payment_stub
    resp: AcceptPaymentResponse = await payment_stub.AcceptPayment(
        AcceptPaymentRequest(bank_json_data=str(body))
    )
    if resp.code == 200:
        return {}
    else:
        make_http_error(resp)


@router.get(
    "/search",
    response_model=list[dict],
    dependencies=[check_permission("READ_PAYMENT")],
    responses=search_payments_responses,
)
async def search_payments(
    page: int = Query(...), search_items: list[ItemModel] = Query(...)
):
    payment_stub: PaymentServiceStub = app.state.payment_stub
    resp: SearchPaymentsResponse = await payment_stub.SearchPayments(
        SearchPaymentsRequest(
            page=page,
            search_strings=[search_item.to_ItemData() for search_item in search_items],
        )
    )
    if resp.code == 200:
        return [json.loads(payment) for payment in resp.payments]
    else:
        make_http_error(resp)


@router.post(
    "/rule",
    dependencies=[check_permission("CREATE_PAYMENT_RULE")],
    responses=add_payment_rule_responses,
    status_code=status.HTTP_201_CREATED,
)
async def add_payment_rule(payment_rule: PaymentRuleModel):
    payment_stub: PaymentServiceStub = app.state.payment_stub

    resp: AddPaymentRuleResponse = await payment_stub.AddPaymentRule(
        AddPaymentRuleRequest(
            payment_rule.cost.to_DecimalData(),
            cost_rules=[rule.to_CostRuleData() for rule in payment_rule.cost_rules],
        )
    )

    if resp.code == 201:
        return {}
    else:
        make_http_error(resp)
