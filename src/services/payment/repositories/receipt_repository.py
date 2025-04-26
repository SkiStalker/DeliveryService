import os
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
import uuid

from models.item_models import ItemModel

DATABASE_URL = (
    f"mongodb://"
    f"{os.environ.get("MONGO_HOST", "localhost")}"
    ":"
    f"{os.environ.get("MONGO_PORT", "27017")}"
)

DB_PAGE_SIZE = int(os.environ.get("DB_PAGE_SIZE", "1000"))

class ReceiptRepository:
    def __init__(self, connection_string: str = DATABASE_URL, page_size: int  = DB_PAGE_SIZE):
        self._connection_string = connection_string
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None
        self._collection: AsyncIOMotorCollection | None = None
        self._page_size = page_size

    async def connect(self):
        self._client = AsyncIOMotorClient(self._connection_string)
        self._db = self._client["company"]
        self._collection = self._db["receipt"]

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

    async def add_receipt(self, receipt: dict):
        receipt["_id"] = str(uuid.uuid4())
        resp = await self._collection.insert_one(receipt)
        
        if resp.acknowledged:
            return True
        return False
    
    async def search_receipts(self, page: int, search_strings: list[ItemModel]) -> list[dict]:

        query_object = {
            "$or": [
                {search_string.field: search_string.value}
                for search_string in search_strings
            ]
        }
        
        resp = await self._collection.find(query_object).limit(page * self._page_size).limit(page).to_list()
        
        return resp

