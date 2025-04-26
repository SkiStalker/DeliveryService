import os

import asyncpg
from pydantic import UUID4

from models.cargo_models import CargoModel, CreateCargoModel, UpdateCargoModel


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


class CargoRepository:
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

    async def create_cargo(self, create_cargo_model: CreateCargoModel) -> CargoModel:
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                cargo_dmp = create_cargo_model.model_dump(exclude_none=True)

                created_cargo = await conn.fetchrow(
                    f'INSERT INTO cargo (title, "type", "description", creator_id, weight) VALUES ($1, $2, $3, $4, $5)) RETURNING cargo.id, cargo."type", cargo."description", cargo.creator_id, cargo.weight',
                    **cargo_dmp.values(),
                )
                return CargoModel.from_record(created_cargo)

    async def get_cargo_by_id(self, cargo_id: str) -> CargoModel:
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                cargo_record = conn.fetchrow(
                    """
                    SELECT
                        c.id,
                        c.title,
                        c.\"type\",
                        c.\"description\",
                        c.creator_id,
                        c.weight,
                        d.id AS delivery_id,
                        d.state AS delivery_state
                    FROM company.public.cargo c 
                    LEFT JOIN 
                    company.public.delivery d ON c.id = d.cargo_id
                    WHERE c.id = $1
                    """,
                    cargo_id,
                )
                
                if cargo_record is None:
                    return cargo_record
                
                delivery_id = cargo_record.pop("delivery_id")
                delivery_state = cargo_record.pop("delivery_state")
                if delivery_id is not None and delivery_state is not None:
                    return    CargoModel.from_record(
                            {
                                **row,
                                "delivery": {
                                    "id": delivery_id,
                                    "state": delivery_state,
                                },
                            }
                        )
                    
                else:
                    return CargoModel.from_record(cargo_record)

    async def get_user_cargos(self, user_id: str, page: int) -> list[CargoModel]:
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                rows = await conn.fetch(
                    """
                    SELECT 
                        c.id,
                        c.title,
                        c.\"type\",
                        c.\"description\",
                        c.creator_id,
                        c.weight,
                        d.id AS delivery_id,
                        d.state AS delivery_state
                    FROM 
                        company.public.cargo c
                    LEFT JOIN 
                        company.public.delivery d ON c.id = d.cargo_id
                    WHERE 
                        c.creator_id = $1
                    LIMIT $2
                    OFFSET $3
                    """,
                    user_id,
                    self._db_page_size,
                    page * self._db_page_size,
                )

                cargos_arr = []

                for row in rows:
                    row = dict(row)
                    delivery_id = row.pop("delivery_id")
                    delivery_state = row.pop("delivery_state")
                    if delivery_id is not None and delivery_state is not None:
                        cargos_arr.append(
                            CargoModel.from_record(
                                {
                                    **row,
                                    "delivery": {
                                        "id": delivery_id,
                                        "state": delivery_state,
                                    },
                                }
                            )
                        )
                    else:
                        cargos_arr.append(CargoModel.from_record(row))

                return cargos_arr

    async def update_cargo(self, cargo_id: str, cargo: UpdateCargoModel) -> CargoModel:
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                if cargo is not None:
                    cargo_dmp = cargo.model_dump(exclude_none=True)
                    update_str = ",".join(
                        [
                            f"{key} = ${ind + 2}"
                            for ind, key in enumerate(cargo_dmp.keys())
                        ]
                    )

                    updated_cargo_record = await conn.fetchrow(
                        f"UPDATE company.public.cargo SET {update_str} WHERE id = $1 RETURNING id, title, \"type\", \"description\", creator_id",
                        cargo_id,
                        *cargo_dmp.values(),
                    )

                    if updated_cargo_record is None:
                        return None

                    delivery_record = conn.fetchrow(
                        "SELECT id, state FROM delivery WHERE cargo_id = $1", cargo_id
                    )
                    if delivery_record is not None:
                        CargoModel.from_record(
                            {**updated_cargo_record, "delivery": {**delivery_record}}
                        )
                    else:
                        return CargoModel.from_record(updated_cargo_record)

                else:
                    return await self.get_cargo_by_id(cargo_id)
