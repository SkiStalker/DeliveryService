import os
import asyncpg

from models.delivery_models import (
    CreateDeliveryModel,
    DeliveryModel,
    SearchDeliveryModel,
    UpdateDeliveryModel,
)


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

    async def get_delivery_by_id(self, delivery_id: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                delivery_record = await conn.fetchrow(
                    "SELECT id, state, priority, sender_id, receiver_id, cargo_id, bill_id, send_address_id, receive_address_id from company.public.delivery WHERE id = $1",
                    delivery_id,
                )
                return DeliveryModel.from_record(delivery_record)

    async def create_delivery(self, delivery: CreateDeliveryModel):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                crated_delivery = conn.fetchrow(
                    "INSERT INTO delivery VALUES (state, priority, sender_id, receiver_id, cargo_id) VALUES ('CREATED', $1, $2, $3, $4) RETURNING id, state, priority, sender_id, receiver_id, cargo_id, send_address_id, receive_address_id",
                    delivery.priority,
                    delivery.sender_id,
                    delivery.receiver_id,
                    delivery.cargo_id,
                )
                return DeliveryModel.from_record(crated_delivery)

    async def search_deliveries(self, page: int, delivery: SearchDeliveryModel | None):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                if delivery is not None:
                    delivery_dmp = delivery.model_dump(exclude_none=True)
                    search_str = " and ".join(
                        [
                            f"{key} = ${ind + 3}"
                            for ind, key in enumerate(delivery_dmp.keys())
                        ]
                    )
                    if len(search_str):
                        rows = await conn.fetch(
                            f"SELECT id, state, priority, sender_id, receiver_id, cargo_id, bill_id, send_address_id, receive_address_id from company.public.delivery WHERE {search_str} LIMIT $1 OFFSET $2",
                            self._db_page_size,
                            page * self._db_page_size,
                            *delivery_dmp.values(),
                        )
                    else:
                        rows = await conn.fetch(
                            f"SELECT id, state, priority, sender_id, receiver_id, cargo_id, bill_id, send_address_id, receive_address_id from company.public.delivery LIMIT $1 OFFSET $2",
                            self._db_page_size,
                            page * self._db_page_size,
                        )
                    return [DeliveryModel.from_record(row) for row in rows]
                else:
                    rows = await conn.fetch(
                        f"SELECT id, state, priority, sender_id, receiver_id, cargo_id, bill_id, send_address_id, receive_address_id from company.public.delivery LIMIT $1 OFFSET $2",
                        self._db_page_size,
                        page * self._db_page_size,
                    )
                    return [DeliveryModel.from_record(row) for row in rows]

    async def update_delivery(
        self, delivery_id: str, delivery: UpdateDeliveryModel | None
    ):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                if delivery is not None:
                    delivery_dmp = delivery.model_dump(exclude_none=True)

                    update_str = ",".join(
                        [
                            f"{key} = ${ind + 2}"
                            for ind, key in enumerate(delivery_dmp.keys())
                        ]
                    )

                    if len(update_str):
                        updated_delivery = await conn.fetchrow(
                            f"UPDATE company.public.delivery SET {update_str} WHERE id = $1 RETURNING id, state, priority, sender_id, receiver_id, cargo_id, send_address_id, receive_address_id",
                            delivery_id,
                            *delivery_dmp.values(),
                        )

                        return DeliveryModel.from_record(updated_delivery)
                    else:
                        return await self.get_delivery_by_id(delivery_id)
                else:
                    return await self.get_delivery_by_id(delivery_id)
