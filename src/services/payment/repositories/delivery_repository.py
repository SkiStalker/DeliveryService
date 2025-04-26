import os

import asyncpg

from models.delivery_models import DeliveryModel


DATABASE_URL = (
    f"postgresql://"
    f"{os.environ.get("POSTGRES_USER", "postgres")}"
    ":"
    f"{os.environ.get("POSTGRES_PASSWORD", "postgres")}"
    "@"
    f"{os.environ.get("POSTGRES_HOST", "localhost")}"
    ":"
    f"{os.environ.get("POSTGRES_PORT", "5432")}"
    "/"
    f"{os.environ.get("POSTGRES_DB", "company")}"
)

DB_PAGE_SIZE = int(os.environ.get("DB_PAGE_SIZE", "1000"))


class DeliveryRepository:
    def __init__(
        self, connection_string: str = DATABASE_URL, db_page_size: int = DB_PAGE_SIZE
    ):
        self._connection_string = connection_string
        self._db_pool: asyncpg.Pool | None = None
        self._db_page_size = db_page_size

    async def connect(self):
        self._db_pool = await asyncpg.create_pool(self._connection_string)

    async def disconnect(self):
        await self._db_pool.close()
        self._db_pool = None

    def __del__(self):
        if self._db_pool is not None:
            self._db_pool.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.disconnect()

    async def set_delivery_bill(self, delivery_id: str, bill_id: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                delivery_record = await conn.fetchrow(
                    "UPDATE company.public.delivery SET bill_id = $2 WHERE id = $1 RETURNING id, bill_id",
                    delivery_id,
                    bill_id,
                )
                if bill_id is not None:
                    return True
                return False

    async def get_delivery_by_id(self, delivery_id: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                delivery_record = await conn.fetchrow(
                    """
                    SELECT
                        d.id AS delivery_id,
                        d.priority,
                        c.type AS cargo_type,
                        c.weight AS cargo_weight,
                        sender.postal_code AS sender_postal_code,
                        receiver.postal_code AS receiver_postal_code
                    FROM
                        delivery d
                    JOIN cargo c ON d.cargo_id = c.id
                    JOIN address sender ON d.sender_address_id = sender.id
                    JOIN address receiver ON d.receiver_address_id = receiver.id
                    WHERE d.id = $1
                    """,
                    delivery_id,
                )
                return DeliveryModel.from_record(delivery_record)
