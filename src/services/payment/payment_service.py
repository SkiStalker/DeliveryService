import asyncio
import json
import math
import os
import grpc
from grpc import ServicerContext

from grpc_build.payment_service_pb2_grpc import (
    PaymentServiceServicer,
    add_PaymentServiceServicer_to_server,
)
from models.cost_rule_models import CostRuleModel
from repositories.payment_rule_repository import PaymentRuleRepository
from repositories.receipt_repository import ReceiptRepository
from grpc_build.payment_service_pb2 import (
    AcceptPaymentRequest,
    AcceptPaymentResponse,
    AddPaymentRuleRequest,
    AddPaymentRuleResponse,
    DecimalData,
    MakePaymentRequest,
    MakePaymentResponse,
    PaymentInfoData,
    SearchPaymentsRequest,
    SearchPaymentsResponse,
    StringArray,
)
from models.item_models import ItemModel
from repositories.delivery_repository import DeliveryRepository
from models.decimal_models import DecimalModel
from models.delivery_models import DeliveryModel


def cargo_type_to_coef(cargo_type: str):
    if cargo_type in ["Glass"]:
        return 5
    elif cargo_type in ["Electronic", "Car detail"]:
        return 3
    else:
        return 1


def fit_rule(delivery_model: DeliveryModel, cost_rules: list[dict]):
    for cost_rule in cost_rules:
        match cost_rule["data"]["field"]:
            case "priority":
                delivery_field = delivery_model.priority
            case "cargo_type":
                delivery_field = delivery_model.cargo_type
            case "sender_postal_code":
                delivery_field = delivery_model.sender_postal_code
            case "receiver_postal_code":
                delivery_field = delivery_model.receiver_postal_code
            case "weight":
                delivery_field = delivery_model.weight
            case _:
                raise Exception("Unknown compared field")

        match cost_rule["compare_type"]:
            case "=":
                if cost_rule["data"]["value"] == delivery_field:
                    return True

            case "<":
                if cost_rule["data"]["value"] < delivery_field:
                    return True

            case ">":
                if cost_rule["data"]["value"] > delivery_field:
                    return True

            case "<=":
                if cost_rule["data"]["value"] <= delivery_field:
                    return True

            case ">=":
                if cost_rule["data"]["value"] >= delivery_field:
                    return True

    return False


class PaymentService(PaymentServiceServicer):
    def __init__(
        self,
        payment_rule_rep: PaymentRuleRepository,
        receipt_rep: ReceiptRepository,
        delivery_rep: DeliveryRepository,
    ):
        self._payment_rule_rep = payment_rule_rep
        self._receipt_rep = receipt_rep
        self._delivery_rep = delivery_rep

    async def MakePayment(
        self, request: MakePaymentRequest, context: ServicerContext
    ) -> MakePaymentResponse:
        try:
            delivery_id = request.delivery_id
            delivery_model = await self._delivery_rep.get_delivery_by_id(delivery_id)
            if delivery_model is not None:
                payment_rules = self._payment_rule_rep.get_payment_rules()
                cost: DecimalModel | None = None
                for payment_rule in payment_rules:
                    if fit_rule(delivery_model, payment_rule):
                        cost = DecimalModel(
                            units=payment_rule["cost"]["units"],
                            nanos=payment_rule["cost"]["nanos"],
                            sign=payment_rule["cost"]["sign"],
                        )
                    else:
                        cost = DecimalModel(units=1000, nanos=0, sign=1)

                return MakePaymentResponse(
                    code=200,
                    payment_data=PaymentInfoData(
                        delivery_id=delivery_id,
                        cost=DecimalData(
                            units=int(cost), nanos=(int((cost % 1) * 1000)), sign=1
                        ),
                        currency="RUB",
                        company_bank_account_hash="AABBCCDDEEFF",
                    ),
                )
            else:
                return MakePaymentResponse(
                    code=404, message=f"Delivery with passed id does not exist"
                )
        except Exception as ex:
            return MakePaymentResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )

    async def AcceptPayment(
        self, request: AcceptPaymentRequest, context: ServicerContext
    ) -> AcceptPaymentResponse:
        try:
            bank_data: dict = json.loads(request.bank_json_data)

            delivery_id = bank_data.get("delivery_id", None)
            if delivery_id is None:
                return AcceptPaymentResponse(
                    code=400, message="Can't find suitable field for delivery_id"
                )

            status: str = bank_data.get("status", None)
            if delivery_id is None:
                return AcceptPaymentResponse(
                    code=400, message="Can't find suitable field for delivery_id"
                )

            if status.lower() in ["okay", "ok", "payed", "success"]:
                pass  # TODO Add notifying delivery service

            if await self._receipt_rep.add_receipt(bank_data):
                return AcceptPaymentResponse(code=201)
            else:
                return AcceptPaymentResponse(code=400, message="Can't add receipt")

        except Exception as ex:
            return AcceptPaymentResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )

    async def SearchPayments(
        self, request: SearchPaymentsRequest, context: ServicerContext
    ) -> SearchPaymentsResponse:
        try:
            page = request.page
            search_strings = [
                ItemModel.from_grpc_message(search_string)
                for search_string in request.search_strings
            ]

            find_payments = await self._receipt_rep.search_receipts(
                page, search_strings
            )

            return SearchPaymentsResponse(
                code=200,
                payments=StringArray(
                    arr=[json.dumps(find_payment) for find_payment in find_payments]
                ),
            )
        except Exception as ex:
            return SearchPaymentsResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )

    async def AddPaymentRule(
        self, request: AddPaymentRuleRequest, context: ServicerContext
    ) -> AddPaymentRuleResponse:
        try:
            cost = request.cost
            cost_rules = [CostRuleModel.from_grpc(rule) for rule in request.cost_rules]

            if await self._payment_rule_rep.add_payment_rule(cost, cost_rules):
                return AddPaymentRuleResponse(code=201)
            else:
                return AddPaymentRuleResponse(
                    code=400, message=f"Can't add new payment rule"
                )

        except Exception as ex:
            return AddPaymentRuleResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )


async def serve():

    server = grpc.aio.server()

    async with PaymentRuleRepository() as payment_rule_rep, ReceiptRepository() as receipt_rep, DeliveryRepository() as delivery_rep:

        add_PaymentServiceServicer_to_server(
            PaymentService(payment_rule_rep, receipt_rep, delivery_rep), server
        )
        server.add_insecure_port(
            f"[::]:{os.environ.get("PAYMENT_SERVICE_PORT", 50055)}"
        )
        print(
            f"Async gRPC Server started at port {os.environ.get("PAYMENT_SERVICE_PORT", 50055)}"
        )
        await server.start()
        try:
            await server.wait_for_termination()
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(serve())
