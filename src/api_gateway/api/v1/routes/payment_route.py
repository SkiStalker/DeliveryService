from context import app
from fastapi import APIRouter


router = APIRouter(prefix="/api/v1/payment", tags=["payment"])

@router.get(
    "/",
    response_model=list[DeliveryModel],
    dependencies=[check_permission("READ_DELIVERY")],
    response_model_exclude_unset=True,
    responses=search_deliveries_responses,
)
async def search_deliveries(