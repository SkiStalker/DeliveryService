import os
import asyncpg

from models.user_model import UserModel
from models.group_model import GroupModel


DATABASE_URL = f"postgresql://{os.environ.get("POSTGRES_USER", "postgres")}:{os.environ.get("POSTGRES_PASSWORD", "postgres")}@{os.environ.get("POSTGRES_HOST", "localhost")}:{os.environ.get("POSTGRES_PORT", "5432")}/{os.environ.get("POSTGRES_DB", "company")}"

DB_PAGE_SIZE = int(os.environ.get("DB_PAGE_SIZE", "1000"))

class UserRepository:
    def __init__(self, connection_string: str = DATABASE_URL, db_page_size: int = DB_PAGE_SIZE):
        self._connection_string = connection_string
        self._db_pool: asyncpg.Pool | None = None
        self._db_page_size = db_page_size 
        
    async def connect(self):
        self._db_pool = await asyncpg.create_pool(self._connection_string)
    
    async def disconnect(self):
        await self._db_pool.close()
        self._db_pool = None
    
    
    async def get_all_users(self, page: int):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                rows = await conn.fetch("SELECT account.id, account.username, account.first_name, account.second_name from account WHERE is_active = TRUE LIMIT $1 OFFSET $2", self._db_page_size, page * self._db_page_size)
                
                return [UserModel.from_record(row) for row in rows]
                    
    async def get_user_by_id(self, user_id: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                return UserModel.from_record(await conn.fetchrow("SELECT account.id, account.username, account.first_name, account.second_name, account.patronymic, account.email, account.phone FROM account WHERE id = $1 and is_active = TRUE", user_id))
    
    async def get_user_groups(self, user_id: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                rows = await conn.fetch('SELECT "group".id, "group".name from "group" join account_group on account_group.group_id = "group".id join account on account_group.account_id = account.id WHERE account.id = $1', user_id)
                
                return [GroupModel.from_record(row) for row in rows]
    
    async def get_user_by_username(self, username: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                return UserModel.from_record(await conn.fetchrow("SELECT account.id FROM account WHERE username = $1", username))
    
    async def deactivate_user(self, user_id: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                affected_columns = await conn.execute("UPDATE company.public.account SET is_active = FALSE WHERE id = $1 and is_active = TRUE", user_id)
                return bool(affected_columns.split(" ")[:-1])
    
    async def reactivate_user(self, user_id: str):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                affected_columns = await conn.execute("UPDATE company.public.account SET is_active = TRUE WHERE id = $1 and is_active = FALSE", user_id)
                return bool(affected_columns.split(" ")[:-1])
    
    async def update_user(self, user: UserModel):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                
                usr_dmp = user.model_dump(exclude_none=True)
                usr_dmp.pop("id")
                
                groups = usr_dmp.pop("groups", None)
                
                update_str =  ",".join([f"{key} = ${ind + 2}" for ind, key in enumerate(usr_dmp.keys())])
                
                if len(update_str):
                    updated_user = await conn.fetchrow(f"UPDATE company.public.account SET {update_str} WHERE id = $1 and is_active = TRUE RETURNING id, username,first_name, second_name, patronymic, email, phone", user.id, *usr_dmp.values())
                else:
                    updated_user = await conn.fetchrow("SELECT account.id, account.username, account.first_name, account.second_name, account.patronymic, account.email, account.phone from company.public.account WHERE id = $1 and is_active = TRUE", user.id)
                
                
                if groups is not None:
                    await conn.execute("DELETE FROM account_group WHERE account_id = $1", user.id)
                    group_models = []
                    for group in groups:
                        updated_account_group = await conn.fetchrow(f'INSERT INTO account_group (account_id, group_id) VALUES ($1, $2) RETURNING account_group.id, (SELECT "group".name from "group" WHERE "group".id = account_group.id) as name')
                        if updated_account_group is None:
                            raise ValueError(user)
                        else:
                            group_models.append(GroupModel.from_record(updated_account_group))
                              
                    updated_user_model = UserModel.from_record(updated_user)
                    updated_user_model.groups = group_models
                    return updated_user_model
                else: 
                    return UserModel.from_record(updated_user)
                    
    
    async def create_user(self, user: UserModel):
        async with self._db_pool.acquire() as conn:
            conn: asyncpg.Connection
            async with conn.transaction():
                usr_dmp = user.model_dump(exclude_none=True)
                
                groups = usr_dmp.pop("groups")
                
                insert_keys = ",".join(usr_dmp.keys())
                
                insert_values = ",".join(range(1, len(usr_dmp.keys())))
                
                
                if len(insert_keys) == 0 or len(insert_values) == 0:
                    raise ValueError(user)
                else:
                    created_user = await conn.fetchrow(f"INSERT INTO account ({insert_keys}) VALUES ({insert_values}) RETURNING account.id, account.username, account.first_name, account.second_name, account.patronymic, account.email, account.phone", **usr_dmp.values())
                    
                    group_models = []
                    for group in groups:
                        created_account_group = await conn.fetchrow(f'INSERT INTO account_group (account_id, group_id) VALUES ($1, $2) RETURNING account_group.id, (SELECT "group".name from "group" WHERE "group".id = account_group.id) as name')
                        if created_account_group is None:
                            raise ValueError(user)
                        else:
                            group_models.append(GroupModel.from_record(created_account_group))
                              
                    created_user_model = UserModel.from_record(created_user)
                    created_user_model.groups = group_models
                    return created_user_model

    
    def __del__(self):
        if self._db_pool is not None:
            self._db_pool.close()
            
            
    