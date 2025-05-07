import os
from pydantic import UUID4
import redis.asyncio

from models.user_models import UpdateUserModel, UserModel


REDIS_URL = (
    f"redis://"
    f"{os.environ.get("REDIS_HOST", "localhost")}"
    f":"
    f"{os.environ.get("REDIS_PORT", "6379")}"
)


class UserCache:
    def __init__(self, redis_url: str = REDIS_URL, redis_db: str = "0"):
        self._redis_url = f"{redis_url}/{redis_db}"
        self._redis_client: redis.asyncio.Redis | None = None

    async def connect(self):
        self._redis_client = redis.asyncio.from_url(self._redis_url)

    async def disconnect(self):
        self._redis_client.close()

    def __del__(self):
        if self._redis_client is not None:
            self._redis_client.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.disconnect()

    
    async def get_user_by_id(self, user_id: str):
        resp = await self._redis_client.get(user_id)
        if resp is not None:
            return UserModel(**resp)
        return None
    
    async def add_or_update_user(self, user: UserModel) -> bool:
        return await self._redis_client.set(str(user.id), user.model_dump())
    
    async def del_user(self, user_id: str) -> bool:
        return await self._redis_client.delete(user_id)
