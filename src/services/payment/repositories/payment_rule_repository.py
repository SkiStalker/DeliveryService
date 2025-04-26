import os
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)

from models.decimal_models import DecimalModel
from models.cost_rule_models import CostRuleModel

DATABASE_URL = (
    f"mongodb://"
    f"{os.environ.get("MONGO_HOST", "localhost")}"
    ":"
    f"{os.environ.get("MONGO_PORT", "27017")}"
)


class PaymentRuleRepository:
    def __init__(self, connection_string: str = DATABASE_URL):
        self._connection_string = connection_string
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None
        self._collection: AsyncIOMotorCollection | None = None

    async def connect(self):
        self._client = AsyncIOMotorClient(self._connection_string)
        self._db = self._client["company"]
        self._collection = self._db["cost_rule"]

    async def disconnect(self):
        self._client.close()
        self._client = None

    def __del__(self):
        if self._client is not None:
            self._client.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.disconnect()

    async def add_payment_rule(
        self, cost: DecimalModel, cost_rules: list[CostRuleModel]
    ):
        insert_object = {
            "cost": cost.model_dump(),
            "cost_rules": [cost_rule.model_dump() for cost_rule in cost_rules],
        }
        res = await self._collection.insert_one(insert_object)
        if res.acknowledged:
            return True
        return False

    async def get_payment_rules(self) -> list[dict]:
        return (
            await self._collection.find()
            .sort([("cost.units", -1), ("cost.nanos", -1)])
            .to_list()
        )
