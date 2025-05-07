import os
import asyncpg

from models.user_models import (
    BriefUserModel,
    CreateUserModel,
    UpdateUserModel,
    UserModel,
)
from models.group_models import GroupModel
from clients.redis.user_cache import UserCache


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


class UserRepository:
    def __init__(
        self,
        connection_string: str = DATABASE_URL,
        db_page_size: int = DB_PAGE_SIZE,
        cache_class: UserCache | None = None,
    ):
        self._connection_string = connection_string
        self._db_pool: asyncpg.Pool | None = None
        self._db_page_size = db_page_size
        self._cache = cache_class

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

    async def _get_user_groups_by_user_id(self, conn: asyncpg.Connection, user_id: str):
        return await conn.fetch(
            'SELECT "group".id, "group".name from "group" join account_group on account_group.group_id = "group".id join account on account_group.account_id = account.id WHERE account.id = $1',
            user_id,
        )

    async def _get_user_groups_by_username(
        self, conn: asyncpg.Connection, username: str
    ):
        return await conn.fetch(
            'SELECT "group".id, "group".name from "group" join account_group on account_group.group_id = "group".id join account on account_group.account_id = account.id WHERE account.username = $1',
            username,
        )

    async def search_users(self, page: int, first_name: str, second_name: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():

                first_name = f"%{first_name}%"

                second_name = f"%{second_name}%"

                rows = await conn.fetch(
                    "SELECT account.id, account.username, account.first_name, account.second_name from account WHERE is_active = TRUE and (account.first_name LIKE $3 and account.second_name LIKE $4) LIMIT $1 OFFSET $2",
                    self._db_page_size,
                    page * self._db_page_size,
                    first_name,
                    second_name,
                )

                return [BriefUserModel.from_record(row) for row in rows]

    async def get_user_by_id(self, user_id: str):
        if self._cache is not None:
            cache_res = await self._cache.get_user_by_id(user_id)
            if cache_res is not None:
                return cache_res

        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                user_record = await conn.fetchrow(
                    "SELECT account.id, account.username, account.first_name, account.second_name, account.patronymic, account.email, account.phone FROM account WHERE id = $1 and is_active = TRUE",
                    user_id,
                )
                groups_records = await self._get_user_groups_by_user_id(conn, user_id)
                return UserModel.from_record(
                    {
                        **user_record,
                        "groups": [
                            dict(group_record) for group_record in groups_records
                        ],
                    }
                )

    async def get_user_by_username(self, username: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                user_record = await conn.fetchrow(
                    "SELECT account.id, account.username, account.first_name, account.second_name, account.patronymic, account.email, account.phone FROM account WHERE username = $1 and is_active = TRUE",
                    username,
                )
                groups_records = await self._get_user_groups_by_username(conn, username)
                return UserModel.from_record(
                    {
                        **user_record,
                        "groups": [
                            dict(group_record) for group_record in groups_records
                        ],
                    }
                )

    async def deactivate_user(self, user_id: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                affected_columns = await conn.execute(
                    "UPDATE company.public.account SET is_active = FALSE WHERE id = $1 and is_active = TRUE",
                    user_id,
                )
                if bool(affected_columns.split(" ")[:-1]) is True:
                    if self._cache is not None:
                        await self._cache.del_user(user_id)
                        return True
                return False

    async def reactivate_user(self, user_id: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                affected_columns = await conn.execute(
                    "UPDATE company.public.account SET is_active = TRUE WHERE id = $1 and is_active = FALSE",
                    user_id,
                )
                if bool(affected_columns.split(" ")[:-1]) is not None:
                    if self._cache is not None:
                        await self._cache.add_user(
                            await self.get_user_by_id(user_id)
                        )
                        return True
                return False

    async def update_user(self, user_id: str, user: UpdateUserModel | None):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                if user is not None:  # If we have fields for update
                    usr_dmp = user.model_dump(exclude_none=True)

                    groups = usr_dmp.pop("groups", None)

                    update_str = ",".join(
                        [
                            f"{key} = ${ind + 2}"
                            for ind, key in enumerate(usr_dmp.keys())
                        ]
                    )

                    if len(update_str):  # Update fields
                        updated_user = await conn.fetchrow(
                            f"UPDATE company.public.account SET {update_str} WHERE id = $1 and is_active = TRUE RETURNING id, username, first_name, second_name, patronymic, email, phone",
                            user_id,
                            *usr_dmp.values(),
                        )
                    else:  # Update only groups
                        updated_user = await conn.fetchrow(
                            "SELECT account.id, account.username, account.first_name, account.second_name, account.patronymic, account.email, account.phone from company.public.account WHERE id = $1 and is_active = TRUE",
                            user_id,
                        )

                    if updated_user is None:
                        return None

                    if groups is not None:  # We need update groups
                        await conn.execute(
                            "DELETE FROM account_group WHERE account_id = $1", user_id
                        )
                        group_records = []
                        for group in groups:
                            updated_account_group = await conn.fetchrow(
                                f'INSERT INTO account_group (account_id, group_id) VALUES ($1, $2) RETURNING account_group.id, (SELECT "group".name from "group" WHERE "group".id = account_group.id) as name'
                            )
                            if updated_account_group is None:
                                raise ValueError(user)
                            else:
                                group_records.append(updated_account_group)

                        updated_user_model = UserModel.from_record(
                            {
                                **updated_user,
                                "group": [
                                    dict(group_record)
                                    for group_record in groups_records
                                ],
                            }
                        )
                        if self._cache is not None:
                            await self._cache.add_or_update_user(
                                updated_user_model
                            )
                        return updated_user_model

                    else:  # We dont need update groups
                        groups_records = await self._get_user_groups_by_user_id(
                            conn, user_id
                        )
                        updated_user_model = UserModel.from_record(
                            {
                                **updated_user,
                                "groups": [
                                    dict(group_record)
                                    for group_record in groups_records
                                ],
                            }
                        )
                        if self._cache is not None:
                            self._cache.add_or_update_user(updated_user_model)
                        return updated_user_model

                else:  # We dont update fields and can use simple get request

                    user_model = await self.get_user_by_id(user_id)
                    if self._cache is not None:
                        self._cache.add_or_update_user(user_model)
                    return user_model

    async def create_user(self, user: CreateUserModel):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                usr_dmp = user.model_dump(exclude_none=True)

                groups_ids = usr_dmp.pop("groups_ids")

                insert_keys = ",".join(usr_dmp.keys())

                insert_values = ",".join(range(1, len(usr_dmp.keys())))

                if len(insert_keys) == 0 or len(insert_values) == 0:
                    raise ValueError(user)
                else:
                    created_user = await conn.fetchrow(
                        f"INSERT INTO account ({insert_keys}) VALUES ({insert_values}) RETURNING account.id, account.username, account.first_name, account.second_name, account.patronymic, account.email, account.phone",
                        **usr_dmp.values(),
                    )

                    group_models = []
                    for group_id in groups_ids:
                        created_account_group = await conn.fetchrow(
                            f'INSERT INTO account_group (account_id, group_id) VALUES ($1, $2) RETURNING account_group.id, (SELECT "group".name from "group" WHERE "group".id = account_group.id) as name',
                            created_user.id,
                            group_id,
                        )
                        if created_account_group is None:
                            raise ValueError(user)
                        else:
                            group_models.append(
                                GroupModel.from_record(created_account_group)
                            )

                    created_user_model = UserModel.from_record(created_user)
                    created_user_model.groups = group_models
                    if self._cache is not None:
                        self._cache.add_or_update_user(created_user_model)
                    return created_user_model
