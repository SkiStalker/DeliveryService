import os
import asyncpg

from models.auth_user_model import AuthUserModel


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


class UserRepository:
    def __init__(self, connection_string: str = DATABASE_URL):
        self._connection_string = connection_string
        self._db_pool: asyncpg.Pool | None = None

    async def connect(self):
        self._db_pool = await asyncpg.create_pool(self._connection_string)

    async def disconnect(self):
        await self._db_pool.close()
        self._db_pool = None

    async def get_user_by_username(self, username: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                return AuthUserModel.from_record(
                    await conn.fetchrow(
                        "SELECT account.id, account.username, account.password, account.refresh_token FROM account"
                        "WHERE username = $1 and is_active = TRUE",
                        username,
                    )
                )

    async def get_user_by_id(self, user_id: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                return AuthUserModel.from_record(
                    await conn.fetchrow(
                        "SELECT account.id, account.username, account.password, account.refresh_token FROM account "
                        "WHERE id = $1 and is_active = TRUE",
                        user_id,
                    )
                )

    async def remove_user_refresh_token(self, user_id: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                affected_columns = await conn.execute(
                    "UPDATE company.public.account SET refresh_token = NULL WHERE id = $1 and is_active = TRUE",
                    user_id,
                )
                return bool(affected_columns.split(" ")[:-1])

    async def update_refresh_token(self, user_id: str, refresh_token: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                affected_columns = await conn.execute(
                    "UPDATE company.public.account SET refresh_token = $2 WHERE id = $1 and is_active = TRUE",
                    user_id,
                    refresh_token,
                )
                return bool(affected_columns.split(" ")[:-1])

    async def get_permissions(self, username: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                rows = await conn.fetch(
                    "SELECT permission.name AS permission_name FROM permission JOIN group_permission ON"
                    ' permission.id = group_permission.permission_id JOIN "group"'
                    ' ON group_permission.group_id = "group".id'
                    ' JOIN account_group ON account_group.group_id = "group".id JOIN account ON'
                    " account_group.account_id = account.id"
                    " WHERE account.username = $1 and account.is_active = TRUE",
                    username,
                )

                return {row["permission_name"] for row in rows}

    def __del__(self):
        if self._db_pool is not None:
            self._db_pool.close()
